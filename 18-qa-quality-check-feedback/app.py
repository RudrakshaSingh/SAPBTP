"""
===============================================================================
 PROBLEM 18 -- Q&A API WITH ANSWER QUALITY CHECK AND FEEDBACK
===============================================================================

WHAT THIS DOES
--------------
Puts a quality layer on the HR RAG API. Every answer is checked against the
retrieved documents to confirm it is actually supported (not made up), and comes
back with a confidence level. Employees can then thumbs-up / thumbs-down an
answer, and the team can read the running tally.

THE IDEA: DON'T JUST ANSWER -- VERIFY, THEN LEARN
-------------------------------------------------
    1. Retrieve the relevant chunks and generate a grounded answer.
    2. CHECK it: a strict fact-checker sees only those chunks and rules whether
       the answer is supported; the retrieval score sets a confidence level.
    3. If it is not supported, say the information may not be available rather
       than handing over an answer we could not verify.
    4. Collect thumbs-up / thumbs-down feedback and summarize it.

THE THREE REQUIREMENTS FROM THE PROBLEM STATEMENT
-------------------------------------------------
    A) Answer with a quality check (supported + confidence)  -> verify.py, STEP 6
    B) Collect helpful / not-helpful feedback                -> feedback.py, STEP 7
    C) Summarize helpful vs not helpful                       -> feedback.py, STEP 7

CONSTRAINT: no external database, in-memory only. Chunks live in a list and
feedback in a list, so restarting the server clears everything.

WHERE THINGS LIVE
-----------------
    config.py       STEP 1     Models, chunk size, top-k, confidence bands
    sample_data.py  STEP 2     The two HR documents
    doc_qa.py       STEP 3-4   Chunking, similarity, the store, search
    rag.py          STEP 5     The grounded answer
    verify.py       STEP 6     The support check and confidence   (Req. A)
    feedback.py     STEP 7     Feedback storage and summary         (Req. B, C)
    models.py       STEP 8     Request and response schemas
    app.py          STEP 9-11  Startup and the five endpoints (this file)

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

from config import FALLBACK
from doc_qa import DocumentStore
from feedback import FeedbackStore
from models import (
    AskRequest,
    AskResponse,
    FeedbackRequest,
    FeedbackSummary,
    IngestRequest,
)
from rag import generate_answer
from sample_data import SAMPLE_DOCUMENTS
from verify import check_support


# =============================================================================
# STEP 9 -- STARTUP: BUILD THE STORES AND LOAD THE SAMPLE DOCUMENTS
# =============================================================================
# `lifespan` is FastAPI's startup hook: everything before `yield` runs once when
# the server starts. We embed the HR documents there so /ask works immediately.
#
# Two stores, both in memory only:
#   * docs     -- the embedded HR chunks
#   * feedback -- the list of thumbs-up / thumbs-down received
# =============================================================================

docs: Optional[DocumentStore] = None
feedback = FeedbackStore()


def get_docs() -> DocumentStore:
    """The document store, or a clear error if startup could not build it."""
    if docs is None:
        raise HTTPException(
            status_code=503,
            detail="Document store unavailable. Is GOOGLE_API_KEY set in .env?",
        )
    return docs


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global docs
    docs = DocumentStore()
    for source, text in SAMPLE_DOCUMENTS:
        count = docs.add_document(text, source)
        print(f"Loaded {source}: {count} chunks")
    yield
    docs = None


app = FastAPI(
    title="Q&A API with Answer Quality Check and Feedback",
    description="An HR assistant that verifies every answer against the "
                "retrieved documents and collects thumbs-up / thumbs-down "
                "feedback.",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# STEP 10 -- THE FIVE ENDPOINTS
# =============================================================================
#   GET  /health            is the server alive?
#   POST /ingest            add documents to the knowledge base
#   POST /ask               answer + quality check                 <-- the main one
#   POST /feedback          record thumbs-up / thumbs-down
#   GET  /feedback/summary  totals: helpful vs not helpful
# =============================================================================

@app.get("/health")
def health() -> dict:
    """Health check, plus a summary of what is loaded."""
    if docs is None:
        return {"status": "starting"}
    return {"status": "ok", "documents": len(docs.sources), "chunks": len(docs.chunks)}


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict:
    """Chunk, embed and store one or more documents."""
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

    return {"status": "stored", "ingested": ingested, "total_chunks": len(active.chunks)}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question, then verify the answer against the retrieved docs."""
    active = get_docs()

    # STEP 5 -- generate the grounded answer and keep the chunks it used.
    answer, results = generate_answer(request.question, active)

    # STEP 6 / REQUIREMENT A -- check the answer against exactly those chunks.
    supported, confidence = check_support(answer, results)

    if not supported:
        # Not verified -> don't hand over an answer we couldn't stand behind.
        # The fallback sentence already tells the user it may not be available.
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
    """Record a thumbs-up / thumbs-down and return the updated totals."""
    feedback.record(request.question, request.helpful)
    return FeedbackSummary(**feedback.summary())


@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary() -> FeedbackSummary:
    """How many answers were marked helpful vs not helpful."""
    return FeedbackSummary(**feedback.summary())


# =============================================================================
# STEP 11 -- RUN THE SERVER
# =============================================================================
# This only runs when you type `python app.py`. "app:app" means: the file
# app.py, and the FastAPI variable named app inside it.
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
