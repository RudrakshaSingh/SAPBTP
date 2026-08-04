"""
Problem 16 — Multi-Document Q&A API with Source Filtering (Simplified)

Run:
    pip install -r requirements.txt
    python app2.py
"""

import math
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 3
FALLBACK = "The information is not available in the provided documents."

# --------------- models ---------------

class IngestDocument(BaseModel):
    source: str
    category: str
    text: str

class IngestRequest(BaseModel):
    documents: list[IngestDocument]

class AskRequest(BaseModel):
    question: str
    category: Optional[str] = None

class GroundedAnswer(BaseModel):
    answer: str
    used_extracts: list[int] = []

class IngestedDocument(BaseModel):
    source: str
    category: str
    chunks: int

class IngestResponse(BaseModel):
    status: str
    ingested: list[IngestedDocument]
    total_chunks: int

class AskResponse(BaseModel):
    answer: str
    category_searched: str
    sources_used: list[str]

# --------------- sample documents ---------------

SAMPLE_DOCUMENTS = [
    ("hr_leave_policy.txt", "HR", """
Annual Leave: Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per month.

Casual Leave: Employees receive 7 days of casual leave per calendar year for short personal absences. Casual leave does not carry forward.

Carry Forward: A maximum of 6 unused annual leave days may be carried forward into the next calendar year. Must be used before 31 March.

Sick Leave: Employees receive 12 days of paid sick leave per calendar year. Absence of 3 or more consecutive days requires a medical certificate.
"""),
    ("hr_employment_terms.txt", "HR", """
Working Hours: Standard working hours are 9 hours per day including a 1-hour break, between 9:00 and 19:00. Core hours are 11:00 to 16:00.

Notice Period: An employee resigning must serve a notice period of 60 days. Employees on probation serve 15 days.

Probation: New employees serve a probation period of 6 months. Probation may be extended once by up to 3 months.

Work From Home: All eligible employees may work from home for up to 2 days per week. A one-time home-office allowance of 15,000 INR is paid after confirmation.
"""),
    ("it_faq.txt", "IT", """
Resetting Your Password: Go to the self-service portal at portal.company.local and click Reset Password. Enter your employee ID and the one-time code sent to your mobile. New password must be at least 12 characters. Passwords expire every 90 days.

Account Lockout: Five failed sign-in attempts lock the account for 30 minutes. The helpdesk can unlock it sooner after verifying identity over a video call.

Email Access: Mailboxes are 50 GB. Mail older than 24 months is archived automatically.
"""),
    ("it_network_faq.txt", "IT", """
VPN Disconnects: If the VPN keeps disconnecting, switch from automatic protocol to TCP in client settings. Move to the 5 GHz band on your router. The VPN client disconnects after 12 hours and after 30 minutes of inactivity.

Wi-Fi and Guest Access: The office network is CORP-SECURE, joined with your domain account. Guest access expires after 24 hours.

Hardware Replacement: Laptops are replaced every 4 years, or sooner if a hardware fault is confirmed.
"""),
    ("finance_travel_policy.txt", "Finance", """
Booking Business Travel: Domestic travel is booked through the travel desk at least 7 days in advance. Grade M3 and above travel by air; others by train AC 2-tier.

Daily Allowance: The daily meal allowance on business trips is 1,800 INR for metro cities and 1,200 INR elsewhere. Hotel limit is 6,000 INR per night in metro cities and 4,000 INR elsewhere.

Local Transport: Personal-vehicle use is reimbursed at 12 INR per kilometre against a trip log.
"""),
    ("finance_reimbursement_rules.txt", "Finance", """
Claim Deadlines: Every reimbursement claim must be submitted within 30 days of the expense date. Approved claims are paid with the next payroll run within 15 working days.

Travel Reimbursement Limit: The total travel reimbursement limit is 50,000 INR per employee per quarter. Claims beyond that need department head approval.

Receipts: Any single expense above 500 INR needs a scanned receipt showing vendor, date and amount.

Phone Allowance: A monthly phone allowance of 1,000 INR is paid to employees in client-facing roles. Home internet is not reimbursed.
"""),
]

# --------------- in-memory store ---------------

# each item: {"source": str, "category": str, "text": str, "embedding": list[float]}
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

def ingest_document(source: str, category: str, text: str):
    """Helper to chunk, embed, and store a document with its category."""
    pieces = splitter.split_text(text)
    vectors = embeddings_model.embed_documents(pieces)
    for t, vec in zip(pieces, vectors):
        chunks_store.append({"source": source, "category": category, "text": t, "embedding": vec})
    return len(pieces)

# --------------- app ---------------

app = FastAPI(
    title="Multi-Document Q&A API with Source Filtering",
    description="Answers HR, IT and Finance questions using RAG, with an optional category filter applied before retrieval.",
    version="1.0.0",
)

@app.on_event("startup")
def seed_sample_docs():
    """Auto-load sample documents on startup."""
    for source, category, text in SAMPLE_DOCUMENTS:
        count = ingest_document(source, category, text)
        print(f"Seeded {source} [{category}]: {count} chunks")

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Multi-Document Q&A API! Visit /docs for interactive documentation."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sources")
def sources():
    """List every stored category with its chunk count and source documents."""
    categories_seen: dict[str, list[dict]] = {}
    for chunk in chunks_store:
        cat = chunk["category"]
        if cat not in categories_seen:
            categories_seen[cat] = []
        categories_seen[cat].append(chunk)

    categories = []
    for cat, cat_chunks in categories_seen.items():
        cat_sources = list(dict.fromkeys(c["source"] for c in cat_chunks))
        categories.append({"category": cat, "chunks": len(cat_chunks), "sources": cat_sources})

    return {"categories": categories, "total_chunks": len(chunks_store)}

@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    results = []
    for doc in req.documents:
        count = ingest_document(doc.source, doc.category, doc.text)
        results.append(IngestedDocument(source=doc.source, category=doc.category, chunks=count))
    return IngestResponse(status="stored", ingested=results, total_chunks=len(chunks_store))

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # step 1: filter chunks by category if provided
    if req.category:
        # check if category exists (case-insensitive)
        known_categories = list(dict.fromkeys(c["category"] for c in chunks_store))
        matched = None
        for cat in known_categories:
            if cat.strip().casefold() == req.category.strip().casefold():
                matched = cat
                break

        if matched is None:
            available = ", ".join(known_categories) or "none yet"
            return AskResponse(
                answer=f"No documents are stored under category '{req.category}'. Available categories: {available}.",
                category_searched=req.category,
                sources_used=[],
            )

        candidates = [c for c in chunks_store if c["category"] == matched]
        category_searched = matched
    else:
        candidates = chunks_store
        category_searched = "all"

    # step 2: embed the question
    q_vec = embeddings_model.embed_query(req.question)

    # step 3: find top 3 similar chunks from candidates
    scored = []
    for chunk in candidates:
        score = cosine_similarity(q_vec, chunk["embedding"])
        scored.append((chunk, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    top3 = scored[:TOP_K]

    if not top3:
        return AskResponse(
            answer=FALLBACK,
            category_searched=category_searched,
            sources_used=[],
        )

    # step 4: build context string with numbered extracts
    context = "\n\n".join(
        f"[Extract {i+1} -- category: {c['category']} -- source: {c['source']}]\n{c['text']}"
        for i, (c, _) in enumerate(top3)
    )

    # step 5: ask gemini with structured output
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    prompt = (
        "You are an internal knowledge-base assistant covering HR, IT and Finance.\n"
        "Answer the question using ONLY the extracts below.\n"
        "If the answer is not in the extracts, reply exactly: "
        f"'{FALLBACK}'\n"
        "In used_extracts, list only the extract numbers you actually used. "
        "If answering with the fallback, leave used_extracts empty.\n\n"
        f"Extracts:\n{context}\n\n"
        f"Question: {req.question}"
    )
    result = llm.with_structured_output(GroundedAnswer).invoke(prompt)

    # step 6: collect sources only from extracts the model actually used
    if result.used_extracts:
        sources_used = list(dict.fromkeys(
            top3[i - 1][0]["source"] for i in result.used_extracts if 1 <= i <= len(top3)
        ))
    else:
        sources_used = []

    return AskResponse(answer=result.answer, category_searched=category_searched, sources_used=sources_used)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app2:app", host="127.0.0.1", port=8000, reload=True)
