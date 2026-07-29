"""
Standalone version of Problem 16: Multi-Document Q&A API with Source Filtering.

This file contains the settings, sample data, API models, in-memory document
store, category-filtered retrieval, RAG pipeline, and FastAPI application.
It does not import config.py, doc_qa.py, models.py, rag.py, or sample_data.py.

Run:
    pip install -r requirements.txt
    python app1.py

Then open http://localhost:8000/docs.
"""

from __future__ import annotations

import math
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field


# =============================================================================
# SETTINGS
# =============================================================================

load_dotenv()

CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
TOP_K = 3

FALLBACK = "The information is not available in the provided documents."


# =============================================================================
# SAMPLE DOCUMENTS
# =============================================================================

HR_LEAVE_POLICY = """
Annual Leave

Every confirmed full-time employee is entitled to 18 days of paid annual leave
per calendar year. Leave accrues at 1.5 days per completed month of service.

Casual Leave

In addition to annual leave, employees receive 7 days of casual leave per
calendar year for short personal absences. Casual leave is taken in blocks of no
more than 2 consecutive days and does not carry forward.

Applications for annual leave must be raised in the HR portal at least 5 working
days before the first day of leave.

Carry Forward

A maximum of 6 unused annual leave days may be carried forward into the next
calendar year. Carried-forward days must be used before 31 March.

Sick Leave

Employees receive 12 days of paid sick leave per calendar year. Absence of 3 or
more consecutive days requires a medical certificate.
"""

HR_EMPLOYMENT_TERMS = """
Working Hours

Standard working hours are 9 hours per day including a 1-hour break, between
9:00 and 19:00. Core hours during which every employee must be available are
11:00 to 16:00.

Notice Period

An employee resigning from the company must serve a notice period of 60 days.
Employees still on probation serve 15 days.

Probation

New employees serve a probation period of 6 months. Probation may be extended
once, by up to 3 months.

Work From Home

All eligible employees may work from home for up to 2 days per week. A one-time
home-office allowance of 15,000 INR is paid after confirmation. Internet charges
are not reimbursed.
"""

IT_SUPPORT_FAQ = """
Resetting Your Password

Go to the self-service portal at portal.company.local and click Reset Password.
Enter your employee ID and the one-time code sent to your registered mobile
number. The new password must be at least 12 characters and cannot repeat any of
your last 5 passwords. Passwords expire every 90 days.

If the one-time code does not arrive within 5 minutes, raise a ticket with the
IT helpdesk on extension 4400.

Account Lockout

Five failed sign-in attempts lock the account for 30 minutes. The helpdesk can
unlock it sooner after verifying your identity over a video call.

Email Access

Mailboxes are 50 GB. Mail older than 24 months is archived automatically and
stays searchable from the archive folder.
"""

IT_NETWORK_FAQ = """
VPN Disconnects

If the VPN keeps disconnecting, first switch from the automatic protocol to TCP
in the client settings, as unstable Wi-Fi drops UDP sessions quickly. Then move
to the 5 GHz band on your router and disable any other VPN or proxy running on
the machine.

The VPN client disconnects on purpose after 12 hours, and after 30 minutes of
inactivity. Reconnecting is expected in both cases and is not a fault.

If disconnects continue, run the Network Report tool from the company portal and
attach its output to a helpdesk ticket.

Wi-Fi and Guest Access

The office network is CORP-SECURE, joined with your domain account. Guest access
expires after 24 hours.

Hardware Replacement

Laptops are replaced every 4 years, or sooner if a hardware fault is confirmed.
"""

FINANCE_TRAVEL_POLICY = """
Booking Business Travel

Domestic travel is booked through the travel desk at least 7 days in advance.
Employees at grade M3 and above travel by air; all other grades travel by train
in AC 2-tier. International travel needs written approval from the department
head.

Daily Allowance

The daily meal allowance on business trips is 1,800 INR for metro cities and
1,200 INR elsewhere. Receipts are not required for the meal allowance. Hotel
bills must be uploaded within 10 days of returning.

The hotel limit is 6,000 INR per night in metro cities and 4,000 INR elsewhere.

Local Transport

Personal-vehicle use is reimbursed at 12 INR per kilometre against a trip log.
"""

FINANCE_REIMBURSEMENT_RULES = """
Claim Deadlines

Every reimbursement claim is submitted in the finance portal within 30 days of
the expense date. Approved claims are paid with the next payroll run, generally
within 15 working days.

Travel Reimbursement Limit

The total travel reimbursement limit is 50,000 INR per employee per quarter.
Claims beyond that limit require the department head's approval.

Receipts

Any single expense above 500 INR needs a scanned receipt showing the vendor,
the date and the amount.

Internet and Phone

A monthly phone allowance of 1,000 INR is paid to employees in client-facing
roles. Home internet is not reimbursed for any grade.
"""

SAMPLE_DOCUMENTS = [
    ("hr_leave_policy.txt", "HR", HR_LEAVE_POLICY),
    ("hr_employment_terms.txt", "HR", HR_EMPLOYMENT_TERMS),
    ("it_faq.txt", "IT", IT_SUPPORT_FAQ),
    ("it_network_faq.txt", "IT", IT_NETWORK_FAQ),
    ("finance_travel_policy.txt", "Finance", FINANCE_TRAVEL_POLICY),
    ("finance_reimbursement_rules.txt", "Finance", FINANCE_REIMBURSEMENT_RULES),
]


# =============================================================================
# API REQUEST AND RESPONSE MODELS
# =============================================================================

class DocumentIn(BaseModel):
    source: str = Field(min_length=1, description="File name, e.g. it_faq.txt")
    category: str = Field(min_length=1, description="Knowledge area, e.g. HR")
    text: str = Field(min_length=1, description="The full text of the document")


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    category: Optional[str] = Field(
        default=None,
        description="Restrict the search to one category. Omit to search all.",
    )


class AskResponse(BaseModel):
    answer: str
    category_searched: str
    sources_used: List[str]


# =============================================================================
# CHUNKING, EMBEDDING, AND CATEGORY-FILTERED RETRIEVAL
# =============================================================================

def chunk_text(text: str) -> List[str]:
    """Split one document into retrieval-sized pieces."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [piece.strip() for piece in splitter.split_text(text) if piece.strip()]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return cosine similarity between two embedding vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def normalise(category: str) -> str:
    """Make category matching case-insensitive and whitespace-tolerant."""
    return category.strip().casefold()


@dataclass
class Chunk:
    """One embedded piece of a document and its source category."""

    source: str
    category: str
    text: str
    embedding: List[float]


class DocumentStore:
    """In-memory document chunks with category filtering before scoring."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    def add_document(self, text: str, source: str, category: str) -> int:
        """Chunk, embed, and store one document under its category."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        vectors = self.embeddings.embed_documents(pieces)
        for piece, vector in zip(pieces, vectors):
            self.chunks.append(
                Chunk(
                    source=source,
                    category=category.strip(),
                    text=piece,
                    embedding=vector,
                )
            )
        return len(pieces)

    @property
    def sources(self) -> List[str]:
        """Return distinct document names in their insertion order."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    @property
    def categories(self) -> List[str]:
        """Return distinct categories in their insertion order."""
        return list(dict.fromkeys(chunk.category for chunk in self.chunks))

    def resolve_category(self, category: str) -> Optional[str]:
        """Return the stored spelling for a category, or None if it is absent."""
        key = normalise(category)
        for chunk in self.chunks:
            if normalise(chunk.category) == key:
                return chunk.category
        return None

    def search(
        self,
        question: str,
        category: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Filter by category first, then return the top similar chunks."""
        candidates = self.chunks
        if category is not None:
            key = normalise(category)
            candidates = [
                chunk
                for chunk in self.chunks
                if normalise(chunk.category) == key
            ]

        if not candidates:
            return []

        query_vector = self.embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in candidates
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]


# =============================================================================
# GROUNDED RAG ANSWERING
# =============================================================================

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an internal knowledge-base assistant covering HR, IT and "
            "finance. Answer employees using ONLY the extracts supplied below.\n\n"
            "Rules:\n"
            "1. Use only the extracts. Never rely on your own knowledge and "
            "never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, amounts) "
            "rather than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
            "4. That same sentence also applies when the extracts you were "
            "given cannot answer the question, even if you suspect another "
            "department's documents could -- the search was deliberately "
            "restricted to one category.\n"
            "Answer in two or three sentences of plain prose. Do not begin with "
            "a preamble such as 'Based on the context'.",
        ),
        (
            "human",
            "Extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Question: {question}",
        ),
    ]
)


def format_context(results: List[Tuple[Chunk, float]]) -> str:
    """Format retrieved chunks as numbered, labelled extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- category: {chunk.category} -- source: {chunk.source}]\n"
        f"{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


def answer_question(
    question: str,
    store: DocumentStore,
    category: Optional[str] = None,
    top_k: int = TOP_K,
) -> Tuple[str, List[str]]:
    """Answer with retrieved text and return the ranked source documents."""
    results = store.search(question, category=category, top_k=top_k)
    if not results:
        return FALLBACK, []

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = RAG_PROMPT | model | StrOutputParser()
    answer = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
        }
    ).strip()

    if not answer or answer == FALLBACK:
        return answer or FALLBACK, []

    sources = list(dict.fromkeys(chunk.source for chunk, _score in results))
    return answer, sources


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

store: Optional[DocumentStore] = None


def get_store() -> DocumentStore:
    """Return the initialized store or a useful startup error."""
    if store is None:
        raise HTTPException(
            status_code=503,
            detail="Document store unavailable. Is GOOGLE_API_KEY set in .env?",
        )
    return store


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create the in-memory store and load the six sample documents."""
    global store
    store = DocumentStore()
    for source, category, text in SAMPLE_DOCUMENTS:
        count = store.add_document(text, source, category)
        print(f"Loaded {source} [{category}]: {count} chunks")
    yield
    store = None


app = FastAPI(
    title="Multi-Document Q&A API with Source Filtering",
    description=(
        "Answers HR, IT and Finance questions using RAG, with an optional "
        "category filter applied before retrieval."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    """Return server and in-memory store status."""
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
    """Chunk, embed, and store one or more documents under their categories."""
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
    """List every stored category with its chunk count and source documents."""
    active = get_store()
    categories = []

    for category in active.categories:
        chunks = [chunk for chunk in active.chunks if chunk.category == category]
        categories.append(
            {
                "category": category,
                "chunks": len(chunks),
                "sources": list(dict.fromkeys(chunk.source for chunk in chunks)),
            }
        )

    return {
        "categories": categories,
        "total_documents": len(active.sources),
        "total_chunks": len(active.chunks),
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Answer a question, optionally restricted to one source category."""
    active = get_store()

    category: Optional[str] = None
    if request.category and request.category.strip():
        category = active.resolve_category(request.category)
        if category is None:
            known = ", ".join(active.categories) or "none yet"
            return AskResponse(
                answer=(
                    f"No documents are stored under category '{request.category}'. "
                    f"Available categories: {known}."
                ),
                category_searched=request.category,
                sources_used=[],
            )

    answer, sources_used = answer_question(
        request.question,
        active,
        category=category,
    )
    return AskResponse(
        answer=answer,
        category_searched=category or "all",
        sources_used=sources_used,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app1:app", host="127.0.0.1", port=8000, reload=True)
