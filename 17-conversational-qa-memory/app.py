"""
===============================================================================
 PROBLEM 17 -- CONVERSATIONAL Q&A API WITH PER-SESSION MEMORY
===============================================================================

WHAT THIS DOES
--------------
Turns the RAG API into a chatbot that remembers the conversation. An employee
can ask a follow-up like "And can I carry them over?" and still get a correct,
grounded answer, because the API knows "them" means the annual leave from the
question before.

THE IDEA: CONVERSATIONAL RAG
----------------------------
Retrieval only works on self-contained questions -- a search engine has no idea
what "them" is. So for every message we:

    1. Look at the conversation history for this session.
    2. Rewrite the follow-up into a standalone question
       ("And can I carry them over?" -> "Can annual leave be carried over?").
    3. Run normal RAG on that standalone question.
    4. Remember this question and answer, so the NEXT follow-up works too.

THE THREE REQUIREMENTS FROM THE PROBLEM STATEMENT
-------------------------------------------------
    A) Keep a separate history per session          -> sessions.py, STEP 5
    B) Rewrite the follow-up using that history      -> rag.py,      STEP 6
    C) Answer with RAG and save the new turn         -> rag.py STEP 7 + /chat

CONSTRAINT: no external database, in-memory only. Sessions live in a dict and
chunks in a list, so restarting the server clears everything.

WHERE THINGS LIVE
-----------------
    config.py       STEP 1     Models, chunk size, top-k, history window
    sample_data.py  STEP 2     The two HR documents
    doc_qa.py       STEP 3-4   Chunking, similarity, the store, search
    sessions.py     STEP 5     Per-session conversation history       (Req. A)
    rag.py          STEP 6-7   Follow-up rewriting and grounded answer (Req. B, C)
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
from models import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    MessageOut,
    NewSessionResponse,
)
from rag import answer_question, rewrite_follow_up
from sample_data import SAMPLE_DOCUMENTS
from sessions import SessionStore


# =============================================================================
# STEP 9 -- STARTUP: BUILD THE STORES AND LOAD THE SAMPLE DOCUMENTS
# =============================================================================
# `lifespan` is FastAPI's startup hook: everything before `yield` runs once when
# the server starts. We embed the HR documents there so /chat works immediately.
#
# Two stores, both in memory only:
#   * docs     -- the embedded HR chunks (shared by every conversation)
#   * sessions -- one history per session_id (kept apart from each other)
# =============================================================================

docs: Optional[DocumentStore] = None
sessions = SessionStore()


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
    title="Conversational Q&A API with Memory",
    description="An HR chatbot that remembers each session, rewrites follow-up "
                "questions using the history, and answers with grounded RAG.",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# STEP 10 -- THE FOUR ENDPOINTS
# =============================================================================
#   GET  /health                  is the server alive?
#   POST /session/new             start a conversation, get a session_id
#   POST /chat                    ask a question in a session          <-- main
#   GET  /session/{id}/history    read a conversation back
# =============================================================================

@app.get("/health")
def health() -> dict:
    """Health check, plus a summary of what is loaded."""
    if docs is None:
        return {"status": "starting"}
    return {"status": "ok", "documents": len(docs.sources), "chunks": len(docs.chunks)}


@app.post("/session/new", response_model=NewSessionResponse)
def new_session() -> NewSessionResponse:
    """Create a fresh, empty conversation and hand back its unique id."""
    return NewSessionResponse(session_id=sessions.new_session())


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer one message, using and updating this session's memory."""
    active = get_docs()

    session = sessions.get(request.session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown session_id. Start one with POST /session/new.",
        )

    # REQUIREMENT B -- fill in the blanks in a follow-up using the history.
    # (On the first message the history is empty, so nothing is rewritten.)
    standalone = rewrite_follow_up(request.question, session.messages)

    # REQUIREMENT C -- answer the standalone question, then remember this turn
    # so the NEXT follow-up can lean on it. We store the ORIGINAL question the
    # user typed, not the rewrite -- the history should read like the real chat.
    answer, sources = answer_question(standalone, active)
    sessions.add_turn(request.session_id, request.question, answer)

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        sources_used=sources,
    )


@app.get("/session/{session_id}/history", response_model=HistoryResponse)
def history(session_id: str) -> HistoryResponse:
    """Return every message in one conversation, oldest first."""
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Unknown session_id. Start one with POST /session/new.",
        )

    return HistoryResponse(
        session_id=session_id,
        messages=[MessageOut(role=m.role, content=m.content) for m in session.messages],
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
