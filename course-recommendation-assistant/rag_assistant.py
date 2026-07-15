"""Course Recommendation Assistant (RAG) built with LangChain + Google Gemini.

Pipeline
--------
1. Turn each course dict into a LangChain ``Document`` (rich text + metadata).
2. Embed the documents with Gemini embeddings and index them in a FAISS
   vector store for semantic search.
3. On a question, retrieve the most relevant courses and pass them to Gemini,
   which returns a structured ``RecommendationResponse`` (Pydantic).
4. Enrich the response with source metadata and total learning hours.

Covers the core assignment plus bonuses:
    #1 custom tool -> ``calculate_total_learning_hours``
    #2 conversation history -> ``ConversationHistory``
    #3 Pydantic result -> ``FinalRecommendation``
    #4 source metadata -> attached in ``recommend``
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from courses import courses
from models import (
    FinalRecommendation,
    RecommendationResponse,
    SourceMetadata,
)

load_dotenv()

# Model names are overridable via environment variables so the app keeps
# working as new Gemini versions are released.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

# Fast lookup of a course record by its id.
COURSES_BY_ID: Dict[str, dict] = {c["course_id"]: c for c in courses}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _hours_from_duration(duration: str) -> int:
    """Extract the integer number of hours from a string like '6 hours'."""
    match = re.search(r"\d+", duration or "")
    return int(match.group()) if match else 0


def build_documents() -> List[Document]:
    """Convert the course catalog into embeddable LangChain documents."""
    documents: List[Document] = []
    for course in courses:
        content = (
            f"Course name: {course['course_name']}\n"
            f"Experience level: {course['experience_level']}\n"
            f"Duration: {course['duration']}\n"
            f"Skills taught: {', '.join(course['skills_taught'])}\n"
            f"Prerequisites: {', '.join(course['prerequisites'])}\n"
            f"Description: {course['course_description']}"
        )
        metadata = {
            "course_id": course["course_id"],
            "course_name": course["course_name"],
            "experience_level": course["experience_level"],
            "duration": course["duration"],
            "source": f"courses.py::{course['course_id']}",
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


# --------------------------------------------------------------------------- #
# Bonus #1 - custom tool: total learning hours
# --------------------------------------------------------------------------- #
@tool
def calculate_total_learning_hours(course_ids: List[str]) -> int:
    """Return the total learning hours for the given list of course ids.

    Sums the ``duration`` of every matching course. Unknown ids are ignored.
    """
    total = 0
    for course_id in course_ids:
        course = COURSES_BY_ID.get(course_id)
        if course:
            total += _hours_from_duration(course["duration"])
    return total


# --------------------------------------------------------------------------- #
# Bonus #2 - conversation history
# --------------------------------------------------------------------------- #
class ConversationHistory:
    """A tiny rolling memory of the dialogue used to give the model context."""

    def __init__(self, max_turns: int = 6) -> None:
        self._turns: List[Dict[str, str]] = []
        self._max_turns = max_turns

    def add(self, question: str, answer: str) -> None:
        self._turns.append({"question": question, "answer": answer})
        self._turns = self._turns[-self._max_turns :]

    def as_prompt_text(self) -> str:
        if not self._turns:
            return "No previous conversation."
        lines = []
        for turn in self._turns:
            lines.append(f"User: {turn['question']}")
            lines.append(f"Assistant: {turn['answer']}")
        return "\n".join(lines)

    def clear(self) -> None:
        self._turns.clear()


# --------------------------------------------------------------------------- #
# The assistant
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = """You are a Course Recommendation Assistant for an SAP + AI
learning academy. Recommend courses ONLY from the retrieved catalog context
below. Never invent courses or ids.

Use the learner's experience and goal to pick the best course(s), and order a
sensible learning sequence from beginner to advanced.

Return your answer using the required structured schema:
- recommended_courses: the course ids (e.g. COURSE_001), best first.
- reason: why these courses suit the learner.
- prerequisites: what the learner should know before starting.
- learning_sequence: the ordered course ids to follow, first to last.
- confidence: 0.0 to 1.0 for how well the catalog matches the request.

Retrieved catalog context:
{context}

Conversation so far:
{history}
"""


class CourseRecommendationAssistant:
    """RAG assistant returning structured, source-attributed recommendations."""

    def __init__(self, top_k: int = 4) -> None:
        self._embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
        self._vectorstore = FAISS.from_documents(
            build_documents(), self._embeddings
        )
        self._retriever = self._vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )
        self._llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.2)
        self._structured_llm = self._llm.with_structured_output(
            RecommendationResponse
        )
        self._prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", "{question}")]
        )
        self.history = ConversationHistory()

    def _format_context(self, docs: List[Document]) -> str:
        blocks = []
        for doc in docs:
            blocks.append(
                f"[{doc.metadata['course_id']}] {doc.page_content}"
            )
        return "\n\n".join(blocks)

    def recommend(
        self, question: str, use_history: bool = True
    ) -> FinalRecommendation:
        """Answer a learner question with a structured recommendation."""
        docs = self._retriever.invoke(question)
        context = self._format_context(docs)
        history_text = (
            self.history.as_prompt_text() if use_history else "No previous conversation."
        )

        chain = self._prompt | self._structured_llm
        result: RecommendationResponse = chain.invoke(
            {
                "context": context,
                "history": history_text,
                "question": question,
            }
        )

        # Bonus #4 - attach source metadata for every recommended course.
        sources: List[SourceMetadata] = []
        for course_id in result.recommended_courses:
            course = COURSES_BY_ID.get(course_id)
            if course:
                sources.append(
                    SourceMetadata(
                        course_id=course["course_id"],
                        course_name=course["course_name"],
                        experience_level=course["experience_level"],
                        duration=course["duration"],
                        source=f"courses.py::{course['course_id']}",
                    )
                )

        # Bonus #1 - use the custom tool to compute total learning hours.
        total_hours = calculate_total_learning_hours.invoke(
            {"course_ids": result.recommended_courses}
        )

        final = FinalRecommendation(
            **result.model_dump(),
            sources=sources,
            total_learning_hours=total_hours,
        )

        # Bonus #2 - remember this turn.
        if use_history:
            summary = (
                f"Recommended {', '.join(result.recommended_courses)} "
                f"(~{total_hours}h). {result.reason}"
            )
            self.history.add(question, summary)

        return final


# --------------------------------------------------------------------------- #
# CLI entry point for a quick manual test
# --------------------------------------------------------------------------- #
def _pretty_print(rec: FinalRecommendation) -> None:
    print("\n=== Recommendation ===")
    print("Recommended courses :", ", ".join(rec.recommended_courses))
    print("Reason              :", rec.reason)
    print("Prerequisites       :", "; ".join(rec.prerequisites) or "None")
    print("Learning sequence   :", " -> ".join(rec.learning_sequence))
    print("Confidence          :", f"{rec.confidence:.0%}")
    print("Total learning hours:", rec.total_learning_hours)
    print("Sources:")
    for src in rec.sources:
        print(f"  - {src.course_id} | {src.course_name} ({src.source})")


if __name__ == "__main__":
    assistant = CourseRecommendationAssistant()
    demo_question = (
        "I am an SAP ABAP developer with no AI experience. "
        "Which course should I take first to learn SAP Business AI?"
    )
    print("Q:", demo_question)
    _pretty_print(assistant.recommend(demo_question))
