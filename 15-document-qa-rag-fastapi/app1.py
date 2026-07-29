"""
Standalone version of Problem 15: Document Q&A API using RAG.

This file contains the settings, sample data, request/response models,
in-memory document store, retrieval pipeline, RAG pipeline, and FastAPI app.
It does not import config.py, doc_qa.py, models.py, rag.py, or sample_data.py.

Run:
    pip install -r requirements.txt
    python app1.py

Then open http://localhost:8000/docs.
"""

from __future__ import annotations

import math
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# SETTINGS
# =============================================================================

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 3

SEED_SAMPLE_DOCS = os.getenv("SEED_SAMPLE_DOCS", "true").lower() not in {
    "false",
    "0",
    "no",
}

FALLBACK = "The information is not available in the provided documents."


# =============================================================================
# SAMPLE DOCUMENTS
# =============================================================================

HR_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.
Employees serving their probation period earn leave from day one but may only
apply for it after confirmation.

Applications for annual leave must be raised in the HR portal at least 5 working
days before the first day of leave. Any period of more than 5 consecutive
working days needs approval from both the reporting manager and the department
head.

Carry Forward

A maximum of 6 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March, after which
they lapse without compensation. Unused leave beyond the 6-day limit is not
encashable.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. Sick leave does
not carry forward. Absence of 3 or more consecutive days requires a medical
certificate from a registered practitioner, submitted within 7 days of returning
to work.

Public Holidays

The company observes 10 public holidays each year. The list is published every
December for the following year. Public holidays that fall on a weekend are not
compensated with an additional day off.
"""

REMOTE_WORK_POLICY = """
Work From Home

All eligible employees may work from home for up to 2 days per week. The
remaining 3 days are worked from the assigned office location. Teams choose
their own anchor day, on which every member is expected in the office.

Eligibility begins after the probation period ends. Employees in roles that
require physical presence, such as lab and facilities roles, are not eligible.

Requesting Remote Days

Remote days are booked in the HR portal by the end of the previous week. A
manager may recall an employee to the office for a client visit, an audit or a
team event with at least 48 hours of notice.

Fully Remote Arrangements

A fully remote arrangement is possible for a maximum of 90 days per year, for
example when an employee relocates temporarily. It requires written approval
from the department head and the HR business partner before travel.

Equipment and Expenses

The company provides a laptop and a headset to every remote worker. A one-time
home-office allowance of 15,000 INR is available after confirmation. Internet
charges are not reimbursed.
"""

EMPLOYMENT_TERMS = """
Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days. The notice period begins on the date
the resignation is acknowledged by the reporting manager in the HR portal, not
on the date the email is sent.

Notice may be shortened only with written approval from the department head.
Unserved days are recovered from the final settlement at the employee's basic
salary rate.

Final Settlement

The full and final settlement is paid within 45 days of the last working day. It
covers unpaid salary, encashable leave and any reimbursements already approved.
Company assets, including the laptop and access cards, must be returned on or
before the last working day.

Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Probation

New employees serve a probation period of 6 months. Confirmation follows a
review by the reporting manager. Probation may be extended once, by up to 3
months, with written reasons shared with the employee.
"""

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", HR_POLICY),
    ("remote_work_policy.txt", REMOTE_WORK_POLICY),
    ("employment_terms.txt", EMPLOYMENT_TERMS),
]


# =============================================================================
# API REQUEST AND RESPONSE MODELS
# =============================================================================

class DocumentIn(BaseModel):
    source: str = Field(description="File name shown in sources_used, e.g. hr_policy.txt")
    text: str = Field(description="The full plain text of the document")

    @field_validator("source", "text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class IngestedDocument(BaseModel):
    source: str
    chunks: int


class IngestResponse(BaseModel):
    status: str
    ingested: List[IngestedDocument]
    total_chunks: int


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(
        default=TOP_K,
        ge=1,
        le=10,
        description="How many extracts to retrieve",
    )

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class AskResponse(BaseModel):
    answer: str
    sources_used: List[str]


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
    """One embedded piece of a document."""

    chunk_id: str
    source: str
    text: str
    embedding: List[float]


class DocumentStore:
    """In-memory document chunks and vector similarity search."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self._doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL,
            task_type="retrieval_document",
        )
        self._query_embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL,
            task_type="retrieval_query",
        )

    def add_document(self, text: str, source: str) -> int:
        """Chunk, embed, and store one document."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        vectors = self._doc_embeddings.embed_documents(pieces)
        for index, (piece, vector) in enumerate(zip(pieces, vectors), start=1):
            self.chunks.append(
                Chunk(
                    chunk_id=f"{source}#chunk-{index}",
                    source=source,
                    text=piece,
                    embedding=vector,
                )
            )
        return len(pieces)

    def clear(self) -> None:
        """Empty the in-memory store."""
        self.chunks.clear()

    @property
    def sources(self) -> List[str]:
        """Return distinct source names in their insertion order."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    def search(
        self,
        question: str,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Return the most similar chunks, with best matches first."""
        if not self.chunks:
            return []

        query_vector = self._query_embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in self.chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]


# =============================================================================
# GROUNDED RAG ANSWERING
# =============================================================================

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an HR assistant. You answer employees using ONLY the policy "
            "extracts supplied in the context.\n\n"
            "Rules:\n"
            "1. Use only the retrieved extracts. Never rely on your own knowledge "
            "and never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, months, "
            "percentages) rather than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
            "4. A question about the world outside these documents always gets "
            "that same sentence.\n"
            "5. In used_extracts, list only the extract numbers you actually drew "
            "on. Retrieval returns the closest three extracts whether or not they "
            "are relevant, so an extract you ignored must not be listed.\n"
            "Answer in two or three sentences of plain prose. Do not add a "
            "preamble such as 'Based on the context'.",
        ),
        (
            "human",
            "Policy extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Question: {question}",
        ),
    ]
)


def format_context(results: List[Tuple[Chunk, float]]) -> str:
    """Format retrieved chunks as numbered policy extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- source: {chunk.source}]\n{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


class GroundedAnswer(BaseModel):
    """Structured output requested from Gemini."""

    answer: str = Field(description="The answer, or the exact fallback sentence.")
    used_extracts: List[int] = Field(
        description=(
            "The extract numbers that actually support the answer, e.g. [1, 3]. "
            "Leave empty when answering with the fallback sentence."
        )
    )


@dataclass
class Answer:
    """A grounded answer and its source documents."""

    answer: str
    sources_used: List[str] = field(default_factory=list)
    chunks_used: List[Tuple[Chunk, float]] = field(default_factory=list)


def answer_question(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Answer:
    """Retrieve relevant text, then answer using only that text."""
    results = store.search(question, top_k=top_k)
    if not results:
        return Answer(answer=FALLBACK)

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = RAG_PROMPT | model.with_structured_output(GroundedAnswer)
    result = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
        }
    )

    text = (result.answer or "").strip()
    if not text or text == FALLBACK:
        return Answer(answer=text or FALLBACK)

    used = [
        results[number - 1]
        for number in dict.fromkeys(result.used_extracts)
        if 1 <= number <= len(results)
    ]
    sources = list(dict.fromkeys(chunk.source for chunk, _score in used))
    return Answer(answer=text, sources_used=sources, chunks_used=used)


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

store: Optional[DocumentStore] = None


def get_store() -> DocumentStore:
    """Return the initialized store or a useful startup error."""
    if store is None:
        raise HTTPException(
            status_code=503,
            detail="Document store unavailable. Is GOOGLE_API_KEY set in .env?",
        )
    return store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create the in-memory store and optionally load the sample documents."""
    global store
    store = DocumentStore()

    if SEED_SAMPLE_DOCS:
        for source, text in SAMPLE_DOCUMENTS:
            count = store.add_document(text, source)
            print(f"Loaded {source}: {count} chunks")

    yield
    store = None


app = FastAPI(
    title="Document Q&A API using RAG",
    description=(
        "Answers HR questions from your documents, using only the passages it "
        "retrieved and naming the ones it used."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home() -> dict:
    """Return a friendly API landing response."""
    return {
        "message": (
            "Welcome to the Document Q&A API using RAG! "
            "Visit /docs for interactive documentation."
        )
    }


@app.get("/health")
def health() -> dict:
    """Return server and in-memory store status."""
    if store is None:
        return {"status": "starting"}
    return {
        "status": "ok",
        "documents": len(store.sources),
        "chunks": len(store.chunks),
    }


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    """Chunk, embed, and store one or more documents."""
    active = get_store()
    ingested = []

    for document in request.documents:
        count = active.add_document(document.text, document.source)
        if count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{document.source}' produced no usable text.",
            )
        ingested.append(IngestedDocument(source=document.source, chunks=count))

    return IngestResponse(
        status="stored",
        ingested=ingested,
        total_chunks=len(active.chunks),
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question using only the ingested documents."""
    active = get_store()
    result = answer_question(request.question, active, top_k=request.top_k)
    return AskResponse(answer=result.answer, sources_used=result.sources_used)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app1:app", host="127.0.0.1", port=8000, reload=True)
