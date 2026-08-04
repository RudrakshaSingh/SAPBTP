"""
Problem 15 — Document Q&A API using RAG (Simplified)

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
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 3
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
    sources_used: list[str]

# --------------- sample documents ---------------

SAMPLE_DOCUMENTS = [
    ("hr_policy.txt", """
Annual Leave: Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per month. Applications must be raised at least 5 working days in advance.

Carry Forward: A maximum of 6 unused annual leave days may be carried forward into the next calendar year. Carried-forward days must be used before 31 March.

Sick Leave: Employees receive 12 days of paid sick leave per calendar year. Sick leave does not carry forward. Absence of 3 or more consecutive days requires a medical certificate.

Public Holidays: The company observes 10 public holidays each year.
"""),
    ("remote_work_policy.txt", """
Work From Home: All eligible employees may work from home for up to 2 days per week. The remaining 3 days are worked from the assigned office. Eligibility begins after probation ends.

Fully Remote: A fully remote arrangement is possible for a maximum of 90 days per year with written approval from the department head.

Equipment: The company provides a laptop and headset. A one-time home-office allowance of 15,000 INR is available after confirmation.
"""),
    ("employment_terms.txt", """
Notice Period: An employee resigning must serve a notice period of 60 days. Employees on probation serve 15 days. Unserved days are recovered from the final settlement.

Final Settlement: The full and final settlement is paid within 45 days of the last working day.

Working Hours: Standard working hours are 9 hours per day including a 1-hour break, between 9:00 and 19:00. Core hours are 11:00 to 16:00.

Probation: New employees serve a probation period of 6 months. Probation may be extended once by up to 3 months.
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

# --------------- app ---------------

app = FastAPI(
    title="Document Q&A API using RAG",
    description="Answers HR questions from your documents, using only the passages it retrieved and naming the ones it used.",
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
    return {"message": "Welcome to Document Q&A RAG API! Visit /docs for interactive documentation."}

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

    # step 3: build context string with numbered extracts
    context = "\n\n".join(
        f"[Extract {i+1} -- source: {c['source']}]\n{c['text']}" for i, (c, _) in enumerate(top3)
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

    # step 5: collect sources only from extracts the model actually used
    if result.used_extracts:
        sources = list(dict.fromkeys(
            top3[i - 1][0]["source"] for i in result.used_extracts if 1 <= i <= len(top3)
        ))
    else:
        sources = []

    return AskResponse(answer=result.answer, sources_used=sources)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app2:app", host="127.0.0.1", port=8000, reload=True)
