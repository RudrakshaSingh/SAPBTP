"""
===============================================================================
 PROBLEM 15 -- DOCUMENT Q&A API USING RAG
===============================================================================

WHAT THIS DOES
--------------
Answers HR questions from company documents. Employees ask "how many annual
leave days do I get?" in plain English instead of scrolling through PDFs, and
get back the policy that is actually written down.

THE IDEA: RAG (Retrieval-Augmented Generation)
----------------------------------------------
An AI has never read your company handbook, so if you just ask it "how many
leave days do I get?" it will invent a number. Instead we:

    1. Cut the documents into small pieces ("chunks").
    2. Find the 3 pieces most related to the question.
    3. Give Gemini ONLY those 3 pieces and say "answer from this, nothing else".

THE THREE REQUIREMENTS FROM THE PROBLEM STATEMENT
-------------------------------------------------
    A) Ingest: chunk the text and embed it into memory   -> doc_qa.py, STEP 4
    B) Retrieve the top 3 chunks by similarity           -> doc_qa.py, STEP 4
    C) Answer from the retrieved text, and cite it       -> rag.py,    STEP 5-7

CONSTRAINT: no external vector database, in-memory only. That is why the chunks
live in an ordinary Python list and we compare them ourselves instead of using
a vector database like Chroma.

WHERE THINGS LIVE
-----------------
    config.py       STEP 1     Models, chunk size, top-k, the fallback sentence
    sample_data.py  STEP 2     The three HR documents
    doc_qa.py       STEP 3-4   Chunking, similarity, the store, search
    rag.py          STEP 5-7   The grounded prompt and the cited answer
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

from config import SEED_SAMPLE_DOCS
from doc_qa import DocumentStore
from models import (
    AskRequest,
    AskResponse,
    IngestedDocument,
    IngestRequest,
    IngestResponse,
)
from rag import answer_question
from sample_data import SAMPLE_DOCUMENTS


# =============================================================================
# STEP 9 -- STARTUP: BUILD THE STORE AND LOAD THE SAMPLE DOCUMENTS
# =============================================================================
# `lifespan` is FastAPI's startup/shutdown hook: everything before `yield` runs
# once when the server starts. We embed the three sample documents there so
# /ask works immediately.
#
# The store is in memory only -- restart the server and it is empty again,
# which is exactly what the "no external vector database" constraint asks for.
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

    if SEED_SAMPLE_DOCS:
        for source, text in SAMPLE_DOCUMENTS:
            count = store.add_document(text, source)
            print(f"Loaded {source}: {count} chunks")

    yield
    store = None


app = FastAPI(
    title="Document Q&A API using RAG",
    description="Answers HR questions from your documents, using only the "
                "passages it retrieved and naming the ones it used.",
    version="1.0.0",
    # docs_url="/docs2",  to move the interactive docs; the default is /docs
    lifespan=lifespan,
)


# =============================================================================
# STEP 10 -- THE FOUR ENDPOINTS
# =============================================================================
#   GET  /          a friendlier landing page than a 404
#   GET  /health    is the server alive?
#   POST /ingest    add documents to the knowledge base
#   POST /ask       ask a question                          <-- the main one
# =============================================================================

@app.get("/")
def home() -> dict:
    """Landing page, so hitting the root gives something friendlier than a 404."""
    return {
        "message": "Welcome to the Document Q&A API using RAG! "
                   "Visit /docs for interactive documentation."
    }


@app.get("/health")
def health() -> dict:
    """Health check, plus a summary of what is loaded."""
    if store is None:
        return {"status": "starting"}
    return {"status": "ok", "documents": len(store.sources), "chunks": len(store.chunks)}


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    """Chunk, embed and store one or more documents."""
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


# =============================================================================
# STEP 11 -- RUN THE SERVER
# =============================================================================
# This only runs when you type `python app.py`. "app:app" means: the file
# app.py, and the FastAPI variable named app inside it.
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
