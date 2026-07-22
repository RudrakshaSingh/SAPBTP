"""Document Q&A API -- FastAPI over the in-memory RAG store.

Needs a Gemini key: copy .env.example to .env and paste your key, then

    uvicorn app:app --reload

Endpoints: GET /health, POST /ingest, POST /ask. Interactive docs at /docs.

The three sample HR documents are loaded at startup so /ask answers straight
away. Set SEED_SAMPLE_DOCS=false to start with an empty store instead.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from doc_qa import TOP_K, DocumentStore, answer_question
from sample_data import SAMPLE_DOCUMENTS

# One process, one store. Everything lives in memory and is lost on restart,
# which is exactly what the brief asks for.
store: DocumentStore | None = None


def get_store() -> DocumentStore:
    """The store, or a 503 if startup could not build it (usually a missing key)."""
    if store is None:
        raise HTTPException(
            status_code=503,
            detail="Document store unavailable. Is GOOGLE_API_KEY set in .env?",
        )
    return store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global store
    store = DocumentStore()

    if os.getenv("SEED_SAMPLE_DOCS", "true").lower() not in {"false", "0", "no"}:
        for source, text in SAMPLE_DOCUMENTS:
            chunks = store.add_document(text, source)
            print(f"Seeded {source}: {chunks} chunks")

    yield
    store = None


app = FastAPI(
    title="Document Q&A API",
    description="Answers HR questions from your documents using RAG.",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------------------------------- #
# Request and response shapes -- FastAPI validates and serialises against these,
# so every reply is valid JSON, including the 422s it raises on bad input.
# --------------------------------------------------------------------------- #
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
    top_k: int = Field(default=TOP_K, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class AskResponse(BaseModel):
    answer: str
    sources_used: List[str]


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks: int


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check, plus what is currently loaded."""
    if store is None:
        return HealthResponse(status="starting", documents=0, chunks=0)
    return HealthResponse(status="ok", documents=len(store.sources), chunks=len(store.chunks))


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    """Chunk, embed and store one or more documents."""
    active = get_store()

    ingested = []
    for document in request.documents:
        chunks = active.add_document(document.text, document.source)
        if chunks == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{document.source}' produced no usable text.",
            )
        ingested.append(IngestedDocument(source=document.source, chunks=chunks))

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
