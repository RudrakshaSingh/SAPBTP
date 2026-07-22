"""Multi-document Q&A API -- FastAPI over the in-memory RAG store, with category filtering.

Needs a Gemini key: copy .env.example to .env and paste your key, then

    uvicorn app:app --reload

Endpoints: GET /health, POST /ingest, POST /ask, GET /sources. Docs at /docs.

Six sample documents across HR, IT and Finance are loaded at startup so /ask
answers straight away. Set SEED_SAMPLE_DOCS=false to start with an empty store.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

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
        for source, category, text in SAMPLE_DOCUMENTS:
            chunks = store.add_document(text, source, category)
            print(f"Seeded {source} [{category}]: {chunks} chunks")

    yield
    store = None


app = FastAPI(
    title="Multi-Document Q&A API",
    description=(
        "Answers HR, IT and Finance questions from your documents using RAG, "
        "with an optional category filter applied before retrieval."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------------------------------- #
# Request and response shapes -- FastAPI validates and serialises against these,
# so every reply is valid JSON, including the 422s it raises on bad input.
# --------------------------------------------------------------------------- #
class DocumentIn(BaseModel):
    source: str = Field(description="File name shown in sources_used, e.g. it_faq.txt")
    category: str = Field(description="Knowledge area, e.g. HR, IT or Finance")
    text: str = Field(description="The full plain text of the document")

    @field_validator("source", "category", "text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class IngestedDocument(BaseModel):
    source: str
    category: str
    chunks: int


class IngestResponse(BaseModel):
    status: str
    ingested: List[IngestedDocument]
    total_chunks: int


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    category: Optional[str] = Field(
        default=None,
        description="Restrict retrieval to one category. Omit to search everything.",
    )
    top_k: int = Field(default=TOP_K, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()

    @field_validator("category")
    @classmethod
    def blank_is_none(cls, value: Optional[str]) -> Optional[str]:
        # "" and "   " mean "no filter", not "a category named nothing".
        if value is None or not value.strip():
            return None
        return value.strip()


class AskResponse(BaseModel):
    answer: str
    category_searched: str = Field(
        description="The category actually searched, or 'all' when unfiltered."
    )
    sources_used: List[str]


class CategorySummary(BaseModel):
    category: str
    chunks: int
    sources: List[str]


class SourcesResponse(BaseModel):
    categories: List[CategorySummary]
    total_documents: int
    total_chunks: int


class HealthResponse(BaseModel):
    status: str
    categories: int
    documents: int
    chunks: int


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness check, plus what is currently loaded."""
    if store is None:
        return HealthResponse(status="starting", categories=0, documents=0, chunks=0)
    return HealthResponse(
        status="ok",
        categories=len(store.categories),
        documents=len(store.sources),
        chunks=len(store.chunks),
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    """Chunk, embed and store one or more documents under their categories."""
    active = get_store()

    ingested = []
    for document in request.documents:
        chunks = active.add_document(document.text, document.source, document.category)
        if chunks == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{document.source}' produced no usable text.",
            )
        ingested.append(
            IngestedDocument(
                source=document.source,
                # Echo the stored spelling: ingesting "it" into an existing "IT"
                # category joins it rather than creating a second one.
                category=active.resolve_category(document.category) or document.category,
                chunks=chunks,
            )
        )

    return IngestResponse(
        status="stored",
        ingested=ingested,
        total_chunks=len(active.chunks),
    )


@app.get("/sources", response_model=SourcesResponse)
def sources() -> SourcesResponse:
    """Every category currently stored, with its chunk count and documents."""
    active = get_store()
    counts: Dict[str, Dict[str, object]] = active.chunk_counts()

    return SourcesResponse(
        categories=[
            CategorySummary(
                category=category,
                chunks=int(counts[category]["chunks"]),
                sources=list(counts[category]["sources"]),  # type: ignore[arg-type]
            )
            # store.categories preserves ingestion order; counts is keyed by it.
            for category in active.categories
        ],
        total_documents=len(active.sources),
        total_chunks=len(active.chunks),
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question, optionally restricted to a single category."""
    active = get_store()

    category: Optional[str] = None
    if request.category is not None:
        category = active.resolve_category(request.category)
        if category is None:
            # An unknown category is a typo or a category nobody has ingested
            # yet. Answering from everything would quietly ignore the filter, so
            # the request is refused -- in the same JSON shape as any other
            # answer, and naming the categories that do exist.
            known = ", ".join(active.categories) or "none yet"
            return AskResponse(
                answer=(
                    f"No documents are stored under category "
                    f"'{request.category}'. Available categories: {known}."
                ),
                category_searched=request.category,
                sources_used=[],
            )

    result = answer_question(
        request.question, active, category=category, top_k=request.top_k
    )
    return AskResponse(
        answer=result.answer,
        category_searched=result.category_searched,
        sources_used=result.sources_used,
    )
