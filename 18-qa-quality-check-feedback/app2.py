"""
Problem 18 — Q&A API with Answer Quality Check & Feedback (Simplified)

Run:
    pip install -r requirements.txt
    python app2.py
"""

import math
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")
CHUNK_SIZE = 300
CHUNK_OVERLAP = 60
TOP_K = 3
CONFIDENCE_HIGH = 0.72
CONFIDENCE_MEDIUM = 0.55
FALLBACK = "The information is not available in the provided documents."

# --------------- models ---------------

class IngestDocument(BaseModel):
    source: str
    text: str

class IngestRequest(BaseModel):
    documents: list[IngestDocument]

class AskRequest(BaseModel):
    question: str

class GroundedAnswer(BaseModel):
    answer: str
    used_extracts: list[int] = []

class IngestedDocument(BaseModel):
    source: str
    chunks: int

class IngestResponse(BaseModel):
    status: str
    ingested: list[IngestedDocument]
    total_chunks: int

class AskResponse(BaseModel):
    answer: str
    supported_by_documents: bool
    confidence: str
    sources_used: list[str]

class FeedbackRequest(BaseModel):
    question: str
    helpful: bool

class FeedbackSummary(BaseModel):
    total: int
    helpful: int
    not_helpful: int

# --------------- sample documents ---------------

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", """
Annual Leave: Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per month.

Carry Forward: A maximum of 10 unused annual leave days may be carried forward into the next calendar year. Must be used before 31 March.

Sick Leave: Employees receive 12 days of paid sick leave per calendar year. Absence of 3 or more consecutive days requires a medical certificate.
"""),
    ("hr_employment_terms.txt", """
Working Hours: Standard working hours are 9 hours per day including a 1-hour break, between 9:00 and 19:00. Core hours are 11:00 to 16:00.

Notice Period: An employee resigning must serve a notice period of 60 days. Employees on probation serve 15 days.

Probation: New employees serve a probation period of 6 months. Probation may be extended once by up to 3 months.

Work From Home: All eligible employees may work from home for up to 2 days per week.
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

# --------------- feedback store ---------------

# each item: {"question": str, "helpful": bool}
feedback_store: list[dict] = []

# --------------- quality check ---------------

def check_support(answer: str, top3: list[tuple], context: str) -> tuple[bool, str]:
    """Verify if the answer is supported by the retrieved documents."""
    if not top3 or answer.strip() == FALLBACK:
        return False, "low"

    # ask Gemini to fact-check the answer against the extracts
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    check_prompt = (
        "You are a strict fact-checker. You are given extracts from HR documents and a proposed answer.\n"
        "Decide whether EVERY factual claim in the answer is directly supported by the extracts.\n"
        "Judge only from the extracts — never use outside knowledge.\n"
        "Reply with exactly one word: SUPPORTED or NOT_SUPPORTED.\n\n"
        f"Extracts:\n{context}\n\n"
        f"Proposed answer: {answer}"
    )
    verdict = llm.invoke(check_prompt).content.strip().upper()

    supported = verdict.startswith("SUPPORTED")
    if not supported:
        return False, "low"

    # confidence based on best similarity score
    best_score = top3[0][1]
    if best_score >= CONFIDENCE_HIGH:
        confidence = "high"
    elif best_score >= CONFIDENCE_MEDIUM:
        confidence = "medium"
    else:
        confidence = "low"

    return True, confidence

# --------------- app ---------------

app = FastAPI(
    title="Q&A API with Answer Quality Check and Feedback",
    description="An HR assistant that verifies every answer against the retrieved documents and collects thumbs-up / thumbs-down feedback.",
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
    return {"message": "Welcome to Q&A Quality Check API! Visit /docs for interactive documentation."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    results = []
    for doc in req.documents:
        count = ingest_document(doc.source, doc.text)
        results.append(IngestedDocument(source=doc.source, chunks=count))
    return IngestResponse(status="stored", ingested=results, total_chunks=len(chunks_store))

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):

    # step 1: embed the question
    q_vec = embeddings_model.embed_query(req.question)

    # step 2: find top 3 similar chunks
    scored = []
    for chunk in chunks_store:
        score = cosine_similarity(q_vec, chunk["embedding"])
        scored.append((chunk, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    top3 = scored[:TOP_K]

    if not top3:
        return AskResponse(answer=FALLBACK, supported_by_documents=False, confidence="low", sources_used=[])

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
        f"Question: {req.question}"
    )
    result = llm.with_structured_output(GroundedAnswer).invoke(prompt)

    # step 5: quality check — verify answer is supported by documents
    supported, confidence = check_support(result.answer, top3, context)

    if not supported:
        return AskResponse(answer=FALLBACK, supported_by_documents=False, confidence=confidence, sources_used=[])

    # step 6: collect sources from used extracts
    if result.used_extracts:
        sources = list(dict.fromkeys(
            top3[i - 1][0]["source"] for i in result.used_extracts if 1 <= i <= len(top3)
        ))
    else:
        sources = list(dict.fromkeys(c["source"] for c, _ in top3))

    return AskResponse(answer=result.answer, supported_by_documents=True, confidence=confidence, sources_used=sources)

@app.post("/feedback", response_model=FeedbackSummary)
def submit_feedback(req: FeedbackRequest):
    """Store one thumbs-up or thumbs-down and return updated totals."""
    feedback_store.append({"question": req.question, "helpful": req.helpful})
    helpful_count = sum(1 for f in feedback_store if f["helpful"])
    return FeedbackSummary(total=len(feedback_store), helpful=helpful_count, not_helpful=len(feedback_store) - helpful_count)

@app.get("/feedback/summary", response_model=FeedbackSummary)
def feedback_summary():
    """Return helpful and not-helpful feedback totals."""
    helpful_count = sum(1 for f in feedback_store if f["helpful"])
    return FeedbackSummary(total=len(feedback_store), helpful=helpful_count, not_helpful=len(feedback_store) - helpful_count)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app2:app", host="127.0.0.1", port=8000, reload=True)
