"""
Standalone version of Problem 18: Q&A API with Answer Quality Check and Feedback.

This file contains settings, sample documents, schemas, in-memory retrieval,
answer generation, support verification, feedback storage, and the FastAPI app.
It does not import config.py, doc_qa.py, feedback.py, models.py, rag.py,
sample_data.py, or verify.py.

Run:
    pip install -r requirements.txt
    python app1.py

Then open http://localhost:8000/docs.
"""

from __future__ import annotations

import math
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
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

CONFIDENCE_HIGH = 0.72
CONFIDENCE_MEDIUM = 0.55

FALLBACK = "The information is not available in the provided documents."


# =============================================================================
# SAMPLE DOCUMENTS
# =============================================================================

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.

Carry Forward

A maximum of 10 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. An absence of 3
or more consecutive days requires a medical certificate.
"""

HR_EMPLOYMENT_TERMS = """
Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days.

Probation

New employees serve a probation period of 6 months. Probation may be extended
once, by up to 3 months.

Work From Home

All eligible employees may work from home for up to 2 days per week.
"""

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("hr_employment_terms.txt", HR_EMPLOYMENT_TERMS),
]


# =============================================================================
# API REQUEST AND RESPONSE MODELS
# =============================================================================

class DocumentIn(BaseModel):
    source: str = Field(min_length=1, description="File name, e.g. hr_policy.txt")
    text: str = Field(min_length=1, description="The full text of the document")


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class AskResponse(BaseModel):
    answer: str
    supported_by_documents: bool
    confidence: str
    sources_used: List[str]


class FeedbackRequest(BaseModel):
    question: str = Field(min_length=1)
    helpful: bool


class FeedbackSummary(BaseModel):
    total: int
    helpful: int
    not_helpful: int


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
    """In-memory document chunks and vector similarity search."""

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
        """Return distinct source names in insertion order."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    def search(
        self,
        question: str,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Return the most similar chunks, with best matches first."""
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
# GROUNDED ANSWER GENERATION
# =============================================================================

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an internal HR assistant. Answer employees using ONLY the "
            "extracts supplied below.\n\n"
            "Rules:\n"
            "1. Use only the extracts. Never rely on your own knowledge and "
            "never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, months) rather "
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


def generate_answer(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Tuple[str, List[Tuple[Chunk, float]]]:
    """Return an answer and the exact chunks retrieved to create it."""
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
    return (answer or FALLBACK), results


# =============================================================================
# ANSWER QUALITY CHECK
# =============================================================================

CHECK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict fact-checker for an HR assistant. You are given "
            "some extracts from HR documents and a proposed answer.\n\n"
            "Decide whether EVERY factual claim in the answer is directly "
            "supported by the extracts. Judge only from the extracts -- never "
            "use outside knowledge.\n\n"
            "Reply with exactly one word: SUPPORTED or NOT_SUPPORTED.",
        ),
        (
            "human",
            "Extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Proposed answer: {answer}",
        ),
    ]
)


def _confidence_from_score(score: float) -> str:
    """Turn the best similarity score into high, medium, or low."""
    if score >= CONFIDENCE_HIGH:
        return "high"
    if score >= CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def check_support(
    answer: str,
    results: List[Tuple[Chunk, float]],
) -> Tuple[bool, str]:
    """Return whether every answer claim is supported, plus confidence."""
    if not results or answer.strip() == FALLBACK:
        return False, "low"

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = CHECK_PROMPT | model | StrOutputParser()
    verdict = chain.invoke(
        {"context": format_context(results), "answer": answer}
    ).strip().upper()

    supported = verdict.startswith("SUPPORTED")
    if not supported:
        return False, "low"

    best_score = results[0][1]
    return True, _confidence_from_score(best_score)


# =============================================================================
# FEEDBACK STORAGE
# =============================================================================

@dataclass
class Feedback:
    """One thumbs-up or thumbs-down for an answer."""

    question: str
    helpful: bool


class FeedbackStore:
    """In-memory feedback entries and aggregate totals."""

    def __init__(self) -> None:
        self._items: List[Feedback] = []

    def record(self, question: str, helpful: bool) -> None:
        """Store one helpful or not-helpful vote."""
        self._items.append(Feedback(question=question, helpful=helpful))

    def summary(self) -> Dict[str, int]:
        """Return feedback totals."""
        helpful = sum(1 for feedback in self._items if feedback.helpful)
        return {
            "total": len(self._items),
            "helpful": helpful,
            "not_helpful": len(self._items) - helpful,
        }


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

docs: Optional[DocumentStore] = None
feedback = FeedbackStore()


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
    title="Q&A API with Answer Quality Check and Feedback",
    description=(
        "An HR assistant that verifies every answer against the retrieved "
        "documents and collects thumbs-up / thumbs-down feedback."
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


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict:
    """Chunk, embed, and store one or more documents."""
    active = get_docs()
    ingested = []

    for document in request.documents:
        count = active.add_document(document.text, document.source)
        if count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{document.source}' produced no usable text.",
            )
        ingested.append({"source": document.source, "chunks": count})

    return {
        "status": "stored",
        "ingested": ingested,
        "total_chunks": len(active.chunks),
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Generate an answer, verify it, then return its quality signal."""
    active = get_docs()
    answer, results = generate_answer(request.question, active)
    supported, confidence = check_support(answer, results)

    if not supported:
        return AskResponse(
            answer=FALLBACK,
            supported_by_documents=False,
            confidence=confidence,
            sources_used=[],
        )

    sources = list(dict.fromkeys(chunk.source for chunk, _score in results))
    return AskResponse(
        answer=answer,
        supported_by_documents=True,
        confidence=confidence,
        sources_used=sources,
    )


@app.post("/feedback", response_model=FeedbackSummary)
def submit_feedback(request: FeedbackRequest) -> FeedbackSummary:
    """Store one thumbs-up or thumbs-down and return updated totals."""
    feedback.record(request.question, request.helpful)
    return FeedbackSummary(**feedback.summary())


@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary() -> FeedbackSummary:
    """Return helpful and not-helpful feedback totals."""
    return FeedbackSummary(**feedback.summary())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app1:app", host="127.0.0.1", port=8000, reload=True)
