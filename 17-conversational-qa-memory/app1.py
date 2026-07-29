"""
Standalone version of Problem 17: Conversational Q&A API with Memory.

This file contains the settings, sample documents, API schemas, in-memory
retrieval store, per-session memory store, follow-up rewriting, RAG answering,
and FastAPI application. It does not import config.py, doc_qa.py, models.py,
rag.py, sample_data.py, or sessions.py.

Run:
    pip install -r requirements.txt
    python app1.py

Then open http://localhost:8000/docs.
"""

from __future__ import annotations

import math
import os
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field


# =============================================================================
# SETTINGS
# =============================================================================

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

CHUNK_SIZE = 300
CHUNK_OVERLAP = 60
TOP_K = 3
MAX_HISTORY_MESSAGES = 6

FALLBACK = "The information is not available in the provided documents."


# =============================================================================
# SAMPLE DOCUMENTS
# =============================================================================

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.
Annual leave is applied for in the HR portal at least 5 working days in advance.

Carry Forward

A maximum of 10 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March, after which
they lapse.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. An absence of 3
or more consecutive days requires a medical certificate. Unused sick leave does
not carry forward.
"""

HR_PARENTAL_LEAVE = """
Maternity Leave

A female employee is entitled to 26 weeks of paid maternity leave for the first
two children. From the third child onwards the entitlement is 12 weeks. Leave
may begin up to 8 weeks before the expected due date.

Paternity Leave

A male employee is entitled to 15 days of paid paternity leave, to be taken
within 3 months of the birth.

Adoption Leave

An employee who legally adopts a child below the age of one year is entitled to
26 weeks of adoption leave, on the same terms as maternity leave. For a child
aged one year or above the entitlement is 12 weeks.
"""

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("hr_parental_leave.txt", HR_PARENTAL_LEAVE),
]


# =============================================================================
# API REQUEST AND RESPONSE MODELS
# =============================================================================

class NewSessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, description="From POST /session/new")
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources_used: List[str]


class MessageOut(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageOut]


# =============================================================================
# CHUNKING, EMBEDDING, AND RETRIEVAL
# =============================================================================

def chunk_text(text: str) -> List[str]:
    """Split one document into retrieval-sized pieces."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [piece.strip() for piece in splitter.split_text(text) if piece.strip()]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return cosine similarity between two embedding vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class Chunk:
    """One embedded piece of a source document."""

    source: str
    text: str
    embedding: List[float]


class DocumentStore:
    """In-memory chunks and vector similarity search."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    def add_document(self, text: str, source: str) -> int:
        """Chunk, embed, and store one document."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        vectors = self.embeddings.embed_documents(pieces)
        for piece, vector in zip(pieces, vectors):
            self.chunks.append(Chunk(source=source, text=piece, embedding=vector))
        return len(pieces)

    @property
    def sources(self) -> List[str]:
        """Return distinct source names in their insertion order."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    def search(
        self,
        question: str,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Return the top similar chunks, best first."""
        if not self.chunks:
            return []

        query_vector = self.embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in self.chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]


# =============================================================================
# PER-SESSION CONVERSATION MEMORY
# =============================================================================

@dataclass
class Message:
    """One line of a conversation."""

    role: str
    content: str


@dataclass
class Session:
    """One conversation and its messages, oldest first."""

    session_id: str
    messages: List[Message] = field(default_factory=list)


class SessionStore:
    """All live conversations, held in memory by session ID."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}

    def new_session(self) -> str:
        """Create a fresh conversation and return its unique ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id=session_id)
        return session_id

    def get(self, session_id: str) -> Optional[Session]:
        """Return a conversation, or None if it has not been created."""
        return self._sessions.get(session_id)

    def add_turn(self, session_id: str, question: str, answer: str) -> None:
        """Append the user question followed by the assistant answer."""
        session = self._sessions[session_id]
        session.messages.append(Message(role="user", content=question))
        session.messages.append(Message(role="assistant", content=answer))


# =============================================================================
# FOLLOW-UP REWRITING AND GROUNDED RAG ANSWERING
# =============================================================================

CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You rewrite a follow-up question so it can be understood on its "
            "own, without the chat history.\n\n"
            "Rules:\n"
            "1. Replace vague references like 'it', 'them' or 'that' with what "
            "they actually refer to in the conversation.\n"
            "2. Do NOT answer the question. Return only the rewritten question.\n"
            "3. Do NOT add any detail that the conversation does not support.\n"
            "4. If the question already stands on its own, return it unchanged.",
        ),
        (
            "human",
            "Conversation so far:\n"
            "----------------\n"
            "{history}\n"
            "----------------\n\n"
            "Follow-up question: {question}\n\n"
            "Standalone question:",
        ),
    ]
)


def format_history(messages: List[Message]) -> str:
    """Format the most recent conversation messages for the rewrite prompt."""
    recent = messages[-MAX_HISTORY_MESSAGES:]
    return "\n".join(
        f"{'User' if message.role == 'user' else 'Assistant'}: {message.content}"
        for message in recent
    )


def rewrite_follow_up(question: str, history: List[Message]) -> str:
    """Rewrite a follow-up as a standalone question using the session history."""
    if not history:
        return question

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = CONDENSE_PROMPT | model | StrOutputParser()
    standalone = chain.invoke(
        {"history": format_history(history), "question": question}
    ).strip()
    return standalone or question


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an internal HR assistant. Answer employees using ONLY the "
            "extracts supplied below.\n\n"
            "Rules:\n"
            "1. Use only the extracts. Never rely on your own knowledge and "
            "never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, weeks) rather "
            "than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
            "Answer in two or three sentences of plain prose. Do not begin with "
            "a preamble such as 'Based on the context'.",
        ),
        (
            "human",
            "Extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Question: {question}",
        ),
    ]
)


def format_context(results: List[Tuple[Chunk, float]]) -> str:
    """Format retrieved chunks as numbered, labelled extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- source: {chunk.source}]\n{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


def answer_question(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Tuple[str, List[str]]:
    """Answer an already-standalone question using retrieved document chunks."""
    results = store.search(question, top_k=top_k)
    if not results:
        return FALLBACK, []

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = RAG_PROMPT | model | StrOutputParser()
    answer = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
        }
    ).strip()

    if not answer or answer == FALLBACK:
        return answer or FALLBACK, []

    sources = list(dict.fromkeys(chunk.source for chunk, _score in results))
    return answer, sources


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

docs: Optional[DocumentStore] = None
sessions = SessionStore()


def get_docs() -> DocumentStore:
    """Return the initialized document store or a useful startup error."""
    if docs is None:
        raise HTTPException(
            status_code=503,
            detail="Document store unavailable. Is GOOGLE_API_KEY set in .env?",
        )
    return docs


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create the document store and load the sample HR documents."""
    global docs
    docs = DocumentStore()
    for source, text in SAMPLE_DOCUMENTS:
        count = docs.add_document(text, source)
        print(f"Loaded {source}: {count} chunks")
    yield
    docs = None


app = FastAPI(
    title="Conversational Q&A API with Memory",
    description=(
        "An HR chatbot that remembers each session, rewrites follow-up "
        "questions using the history, and answers with grounded RAG."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    """Return server and in-memory document-store status."""
    if docs is None:
        return {"status": "starting"}
    return {
        "status": "ok",
        "documents": len(docs.sources),
        "chunks": len(docs.chunks),
    }


@app.post("/session/new", response_model=NewSessionResponse)
def new_session() -> NewSessionResponse:
    """Create a fresh empty conversation."""
    return NewSessionResponse(session_id=sessions.new_session())


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer one question and append the turn to the selected session."""
    active = get_docs()

    session = sessions.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown session_id. Start one with POST /session/new.",
        )

    standalone = rewrite_follow_up(request.question, session.messages)
    answer, sources = answer_question(standalone, active)
    sessions.add_turn(request.session_id, request.question, answer)

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources_used=sources,
    )


@app.get("/session/{session_id}/history", response_model=HistoryResponse)
def history(session_id: str) -> HistoryResponse:
    """Return all messages for a conversation, oldest first."""
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown session_id. Start one with POST /session/new.",
        )

    return HistoryResponse(
        session_id=session_id,
        messages=[
            MessageOut(role=message.role, content=message.content)
            for message in session.messages
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app1:app", host="127.0.0.1", port=8000, reload=True)
