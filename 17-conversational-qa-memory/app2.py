"""
Problem 17 — Conversational Q&A API with Memory (Simplified)

Run:
    pip install -r requirements.txt
    python app2.py
"""

import math
import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")
CHUNK_SIZE = 300
CHUNK_OVERLAP = 60
TOP_K = 3
MAX_HISTORY_MESSAGES = 6
FALLBACK = "The information is not available in the provided documents."

# --------------- models ---------------

class NewSessionResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    question: str

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources_used: list[str]

class MessageOut(BaseModel):
    role: str
    content: str

class HistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageOut]

class GroundedAnswer(BaseModel):
    answer: str
    used_extracts: list[int] = []

# --------------- sample documents ---------------

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", """
Annual Leave: Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per month. Applications must be raised at least 5 working days in advance.

Carry Forward: A maximum of 10 unused annual leave days may be carried forward into the next calendar year. Carried-forward days must be used before 31 March.

Sick Leave: Employees receive 12 days of paid sick leave per calendar year. Absence of 3 or more consecutive days requires a medical certificate. Unused sick leave does not carry forward.
"""),
    ("hr_parental_leave.txt", """
Maternity Leave: A female employee is entitled to 26 weeks of paid maternity leave for the first two children. From the third child onwards the entitlement is 12 weeks. Leave may begin up to 8 weeks before the expected due date.

Paternity Leave: A male employee is entitled to 15 days of paid paternity leave, to be taken within 3 months of the birth.

Adoption Leave: An employee who legally adopts a child below the age of one year is entitled to 26 weeks of adoption leave, on the same terms as maternity leave. For a child aged one year or above the entitlement is 12 weeks.
"""),
]

# --------------- in-memory store ---------------

# each item: {"source": str, "text": str, "embedding": list[float]}
chunks_store: list[dict] = []

embeddings_model = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def ingest_document(source: str, text: str):
    """Helper to chunk, embed, and store a document."""
    pieces = splitter.split_text(text)
    vectors = embeddings_model.embed_documents(pieces)
    for t, vec in zip(pieces, vectors):
        chunks_store.append({"source": source, "text": t, "embedding": vec})
    return len(pieces)

# --------------- session memory ---------------

# sessions dict: session_id -> list of {"role": str, "content": str}
sessions: dict[str, list[dict]] = {}

def rewrite_follow_up(question: str, history: list[dict]) -> str:
    """Rewrite a vague follow-up into a standalone question using chat history."""
    if not history:
        return question

    # format last 6 messages as context
    recent = history[-MAX_HISTORY_MESSAGES:]
    history_text = "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in recent
    )

    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    prompt = (
        "You rewrite a follow-up question so it can be understood on its own, without the chat history.\n"
        "Rules:\n"
        "1. Replace vague references like 'it', 'them' or 'that' with what they refer to.\n"
        "2. Do NOT answer the question. Return ONLY the rewritten question.\n"
        "3. If the question already stands on its own, return it unchanged.\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Follow-up question: {question}\n\n"
        "Standalone question:"
    )
    result = llm.invoke(prompt)
    return result.content.strip() or question

# --------------- app ---------------

app = FastAPI(
    title="Conversational Q&A API with Memory",
    description="An HR chatbot that remembers each session, rewrites follow-up questions using the history, and answers with grounded RAG.",
    version="1.0.0",
)

@app.on_event("startup")
def seed_sample_docs():
    """Auto-load sample HR documents on startup."""
    for source, text in SAMPLE_DOCUMENTS:
        count = ingest_document(source, text)
        print(f"Seeded {source}: {count} chunks")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Conversational Q&A API! Visit /docs for interactive documentation."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/session/new", response_model=NewSessionResponse)
def new_session():
    """Create a fresh empty conversation."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return NewSessionResponse(session_id=session_id)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Answer one question and append the turn to the session history."""
    # validate session
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Unknown session_id. Start one with POST /session/new.")

    history = sessions[req.session_id]

    # step 1: rewrite follow-up into standalone question
    standalone = rewrite_follow_up(req.question, history)

    # step 2: embed and find top 3 similar chunks
    q_vec = embeddings_model.embed_query(standalone)
    scored = []
    for chunk in chunks_store:
        score = cosine_similarity(q_vec, chunk["embedding"])
        scored.append((chunk, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    top3 = scored[:TOP_K]

    if not top3:
        answer = FALLBACK
        history.append({"role": "user", "content": req.question})
        history.append({"role": "assistant", "content": answer})
        return ChatResponse(session_id=req.session_id, answer=answer, sources_used=[])

    # step 3: build context with numbered extracts
    context = "\n\n".join(
        f"[Extract {i+1} -- source: {c['source']}]\n{c['text']}"
        for i, (c, _) in enumerate(top3)
    )

    # step 4: ask gemini with structured output
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    prompt = (
        "You are an HR assistant. Answer the question using ONLY the extracts below.\n"
        "If the answer is not in the extracts, reply exactly: "
        f"'{FALLBACK}'\n"
        "In used_extracts, list only the extract numbers you actually used. "
        "If answering with the fallback, leave used_extracts empty.\n\n"
        f"Extracts:\n{context}\n\n"
        f"Question: {standalone}"
    )
    result = llm.with_structured_output(GroundedAnswer).invoke(prompt)

    # step 5: collect sources from used extracts
    if result.used_extracts:
        sources = list(dict.fromkeys(
            top3[i - 1][0]["source"] for i in result.used_extracts if 1 <= i <= len(top3)
        ))
    else:
        sources = []

    # step 6: save turn to session history
    history.append({"role": "user", "content": req.question})
    history.append({"role": "assistant", "content": result.answer})

    return ChatResponse(session_id=req.session_id, answer=result.answer, sources_used=sources)

@app.get("/session/{session_id}/history", response_model=HistoryResponse)
def get_history(session_id: str):
    """Return all messages for a conversation."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Unknown session_id. Start one with POST /session/new.")

    return HistoryResponse(
        session_id=session_id,
        messages=[MessageOut(role=m["role"], content=m["content"]) for m in sessions[session_id]],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app2:app", host="127.0.0.1", port=8000, reload=True)
