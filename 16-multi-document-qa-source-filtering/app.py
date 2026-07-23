"""
===============================================================================
 PROBLEM 16 -- MULTI-DOCUMENT Q&A API WITH CATEGORY-BASED SOURCE FILTERING
===============================================================================

WHAT THIS DOES
--------------
Answers HR / IT / Finance questions from company documents, and lets you
restrict a question to ONE category so an IT question never gets answered from
the leave policy.

THE IDEA: RAG (Retrieval-Augmented Generation)
----------------------------------------------
An AI has never read your company handbook, so if you just ask it "how many
leave days do I get?" it will invent a number. Instead we:

    1. Cut the documents into small pieces ("chunks").
    2. Find the 3 pieces most related to the question.
    3. Give Gemini ONLY those 3 pieces and say "answer from this, nothing else".

THE THREE REQUIREMENTS FROM THE PROBLEM STATEMENT
-------------------------------------------------
    A) Every chunk remembers its category and source name  -> doc_qa.py, STEP 4
    B) Filter by category BEFORE searching                 -> doc_qa.py, STEP 5
    C) The answer says which source(s) it used             -> rag.py,    STEP 7

CONSTRAINT: no external database, in-memory only. That is why the chunks live
in an ordinary Python list and we compare them ourselves instead of using a
vector database like Chroma.

WHERE THINGS LIVE
-----------------
    config.py       STEP 1     Models, chunk size, top-k, the fallback sentence
    sample_data.py  STEP 2     The six HR / IT / Finance documents
    doc_qa.py       STEP 3-5   Chunking, similarity, the store, filtered search
    rag.py          STEP 6-7   The grounded prompt and the cited answer
    models.py       STEP 8     Request and response schemas
    app.py          STEP 9-11  Startup and the four endpoints (this file)

HOW TO RUN
----------
    pip install -r requirements.txt
    python app.py                       (or: uvicorn app:app --reload)

    Then open http://localhost:8000/docs

Needs a Gemini key in a .env file next to this script:
    GOOGLE_API_KEY=your-key-here
===============================================================================
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException

from doc_qa import DocumentStore
from models import AskRequest, AskResponse, IngestRequest
from rag import answer_question
from sample_data import SAMPLE_DOCUMENTS


# =============================================================================
# STEP 9 -- STARTUP: BUILD THE STORE AND LOAD THE SAMPLE DOCUMENTS
# =============================================================================
# `lifespan` is FastAPI's startup/shutdown hook: everything before `yield` runs
# once when the server starts. We embed the six sample documents there so /ask
# works immediately.
#
# The store is in memory only -- restart the server and it is empty again,
# which is exactly what the "no external database" constraint asks for.
# =============================================================================

store: Optional[DocumentStore] = None


def get_store() -> DocumentStore:
    """The store, or a clear error if startup could not build it."""
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
    for source, category, text in SAMPLE_DOCUMENTS:
        count = store.add_document(text, source, category)
        print(f"Loaded {source} [{category}]: {count} chunks")
    yield
    store = None


app = FastAPI(
    title="Multi-Document Q&A API with Source Filtering",
    description="Answers HR, IT and Finance questions using RAG, with an "
                "optional category filter applied before retrieval.",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# STEP 10 -- THE FOUR ENDPOINTS
# =============================================================================
#   GET  /health    is the server alive?
#   POST /ingest    add documents under a category
#   GET  /sources   list every category and its chunk count
#   POST /ask       ask a question, optionally filtered   <-- the main one
# =============================================================================

@app.get("/health")
def health() -> dict:
    """Health check, plus a summary of what is loaded."""
    if store is None:
        return {"status": "starting"}
    return {
        "status": "ok",
        "categories": len(store.categories),
        "documents": len(store.sources),
        "chunks": len(store.chunks),
    }


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict:
    """Chunk, embed and store one or more documents under their categories."""
    active = get_store()

    ingested = []
    for document in request.documents:
        count = active.add_document(document.text, document.source, document.category)
        if count == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{document.source}' produced no usable text.",
            )
        ingested.append(
            {
                "source": document.source,
                "category": document.category,
                "chunks": count,
            }
        )

    return {
        "status": "stored",
        "ingested": ingested,
        "total_chunks": len(active.chunks),
    }


@app.get("/sources")
def sources() -> dict:
    """Every category currently stored, with its chunk count and documents."""
    active = get_store()

    categories = []
    for category in active.categories:
        chunks = [c for c in active.chunks if c.category == category]
        categories.append(
            {
                "category": category,
                "chunks": len(chunks),
                "sources": list(dict.fromkeys(c.source for c in chunks)),
            }
        )

    return {
        "categories": categories,
        "total_documents": len(active.sources),
        "total_chunks": len(active.chunks),
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question, optionally restricted to a single category."""
    active = get_store()

    category: Optional[str] = None
    if request.category and request.category.strip():
        category = active.resolve_category(request.category)

        # An unknown category is a typo, or an area nobody has uploaded yet.
        # Searching everything would quietly ignore the filter, so we say so --
        # in the same JSON shape as any other answer, and never a crash.
        if category is None:
            known = ", ".join(active.categories) or "none yet"
            return AskResponse(
                answer=f"No documents are stored under category "
                       f"'{request.category}'. Available categories: {known}.",
                category_searched=request.category,
                sources_used=[],
            )

    answer, sources_used = answer_question(request.question, active, category=category)
    return AskResponse(
        answer=answer,
        category_searched=category or "all",
        sources_used=sources_used,
    )


# =============================================================================
# STEP 11 -- RUN THE SERVER
# =============================================================================
# This only runs when you type `python app.py`. "app:app" means: the file
# app.py, and the FastAPI variable named app inside it.
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
