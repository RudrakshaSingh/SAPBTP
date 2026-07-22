"""Document Q&A over HR policies -- retrieval-augmented generation, all in memory.

Pipeline
--------
1.  ``chunk_text``      Requirement A -- split a long document into overlapping chunks.
2.  ``DocumentStore``   Requirement A -- Gemini embeddings held in a plain Python list.
3.  ``DocumentStore.search``  Requirement B -- cosine similarity, top 3 chunks.
4.  ``answer_question`` Requirement C -- grounded answer plus the sources it used.

There is no vector database here on purpose. The corpus is a handful of policy
documents, so a list of vectors and one dot product per chunk is faster to read
and faster to run than any index would be.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

load_dotenv()

# Model names are overridable via environment variables so the app keeps working
# as new Gemini versions are released.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

# Policy documents are written in short paragraphs, so ~800 characters keeps one
# rule (leave entitlement, notice period) inside a single chunk. The overlap
# stops a sentence that straddles a boundary from losing its subject.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

TOP_K = 3

FALLBACK = (
    "The information is not available in the provided documents."
)


# --------------------------------------------------------------------------- #
# Requirement A -- chunking
# --------------------------------------------------------------------------- #
def chunk_text(text: str) -> List[str]:
    """Split one document into retrieval-sized pieces.

    Paragraph and sentence boundaries are tried before a hard character cut, so
    a chunk rarely begins mid-sentence.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [chunk.strip() for chunk in splitter.split_text(text) if chunk.strip()]


# --------------------------------------------------------------------------- #
# Requirement A -- the in-memory store
# --------------------------------------------------------------------------- #
@dataclass
class Chunk:
    """One embedded piece of one document."""

    chunk_id: str
    source: str
    text: str
    embedding: List[float]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Similarity of two vectors, 1.0 when identical in direction.

    Gemini does not promise unit-length vectors, so the magnitudes are divided
    out rather than assumed away.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class DocumentStore:
    """Embedded chunks in a Python list, searched by cosine similarity."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        # Documents and questions are embedded with different task types: the
        # same sentence is stored as an answer but queried as a question, and
        # telling Gemini which role it plays measurably sharpens retrieval.
        self._doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL, task_type="retrieval_document"
        )
        self._query_embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBED_MODEL, task_type="retrieval_query"
        )

    # -- ingestion ---------------------------------------------------------- #
    def add_document(self, text: str, source: str) -> int:
        """Chunk, embed and store one document. Returns the number of chunks."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        # One batched call for the whole document instead of one call per chunk.
        vectors = self._doc_embeddings.embed_documents(pieces)

        start = len(self.chunks)
        for index, (piece, vector) in enumerate(zip(pieces, vectors), start=1):
            self.chunks.append(
                Chunk(
                    chunk_id=f"{source}#chunk-{index}",
                    source=source,
                    text=piece,
                    embedding=vector,
                )
            )
        return len(self.chunks) - start

    def clear(self) -> None:
        self.chunks.clear()

    @property
    def sources(self) -> List[str]:
        """Every distinct document name currently stored, in insertion order."""
        seen: List[str] = []
        for chunk in self.chunks:
            if chunk.source not in seen:
                seen.append(chunk.source)
        return seen

    # -- Requirement B: retrieval ------------------------------------------- #
    def search(self, question: str, top_k: int = TOP_K) -> List[Tuple[Chunk, float]]:
        """Return the ``top_k`` chunks closest to the question, best first."""
        if not self.chunks:
            return []

        query_vector = self._query_embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in self.chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]


# --------------------------------------------------------------------------- #
# Requirement C -- the grounded prompt
# --------------------------------------------------------------------------- #
class GroundedAnswer(BaseModel):
    """What the model must return: the answer, and which extracts produced it."""

    answer: str = Field(description="The answer, or the exact fallback sentence.")
    used_extracts: List[int] = Field(
        description=(
            "The extract numbers that actually support the answer, e.g. [1, 3]. "
            "Leave empty when answering with the fallback sentence."
        )
    )


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an HR assistant. You answer employees using ONLY the policy "
            "extracts supplied in the context.\n\n"
            "Rules:\n"
            "1. Use only the retrieved extracts. Never rely on your own knowledge "
            "and never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, months, "
            "percentages) rather than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
            "4. A question about the world outside these documents always gets "
            "that same sentence.\n"
            "5. In used_extracts, list only the extract numbers you actually drew "
            "on. Retrieval returns the closest three extracts whether or not they "
            "are relevant, so an extract you ignored must not be listed.\n"
            "Answer in two or three sentences of plain prose. Do not add a "
            "preamble such as 'Based on the context'.",
        ),
        (
            "human",
            "Policy extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Question: {question}",
        ),
    ]
)


def format_context(results: List[Tuple[Chunk, float]]) -> str:
    """Render the retrieved chunks, each labelled with the file it came from."""
    return "\n\n".join(
        f"[Extract {rank} -- source: {chunk.source}]\n{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


@dataclass
class Answer:
    """A grounded answer plus the documents behind it."""

    answer: str
    sources_used: List[str] = field(default_factory=list)
    chunks_used: List[Tuple[Chunk, float]] = field(default_factory=list)


def answer_question(question: str, store: DocumentStore, top_k: int = TOP_K) -> Answer:
    """Retrieve, then generate an answer grounded in what was retrieved."""
    results = store.search(question, top_k=top_k)
    if not results:
        return Answer(answer=FALLBACK)

    # temperature=0 keeps the answer pinned to the retrieved text.
    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = RAG_PROMPT | model.with_structured_output(GroundedAnswer)
    result = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
        }
    )

    text = (result.answer or "").strip()

    # An out-of-scope question cites nothing: listing sources next to the
    # fallback sentence would imply the documents were consulted and found to
    # contain an answer.
    if not text or text == FALLBACK:
        return Answer(answer=text or FALLBACK)

    # The numbers are 1-based positions in `results`. Anything outside that range
    # is a citation the model made up, so it is dropped rather than trusted.
    used = [
        results[number - 1]
        for number in dict.fromkeys(result.used_extracts)
        if 1 <= number <= len(results)
    ]

    sources: List[str] = []
    for chunk, _score in used:
        if chunk.source not in sources:
            sources.append(chunk.source)
    return Answer(answer=text, sources_used=sources, chunks_used=used)
