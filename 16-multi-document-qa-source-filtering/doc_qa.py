"""Multi-document Q&A -- retrieval-augmented generation with category filtering.

Pipeline
--------
1.  ``chunk_text``          Requirement A -- split a long document into overlapping chunks.
2.  ``DocumentStore``       Requirement A -- every chunk carries its source *and* its category.
3.  ``DocumentStore.search`` Requirement B -- filter by category first, then score what is left.
4.  ``answer_question``     Requirement C -- grounded answer plus the sources it used.

This builds on hands-on 1. The one structural change is that a ``Chunk`` now
remembers which knowledge area it came from, and the filter is applied *before*
the similarity scoring rather than after: a post-filter would let HR chunks
crowd the top three and hand back one IT chunk when three were asked for.

There is still no vector database. The corpus is a handful of policy documents,
so a list of vectors and one dot product per chunk is faster to read and faster
to run than any index would be.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

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

# Policy and FAQ documents are written in short paragraphs, so ~800 characters
# keeps one rule (leave entitlement, per diem, VPN fix) inside a single chunk.
# The overlap stops a sentence that straddles a boundary from losing its subject.
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
# Requirement A -- the in-memory store, now with metadata
# --------------------------------------------------------------------------- #
@dataclass
class Chunk:
    """One embedded piece of one document, tagged with where it belongs."""

    chunk_id: str
    source: str
    category: str
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


def normalise(category: str) -> str:
    """The lookup key for a category: 'it', ' IT ' and 'It' are one category."""
    return category.strip().casefold()


class DocumentStore:
    """Embedded chunks in a Python list, filtered by category then scored."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        # Categories are whatever was ingested -- there is no hard-coded list of
        # three. This maps the lookup key to the spelling first used at ingest,
        # so "it" asked for at query time answers as "IT" in the response.
        self._category_names: Dict[str, str] = {}
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
    def add_document(self, text: str, source: str, category: str) -> int:
        """Chunk, embed and store one document. Returns the number of chunks."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        key = normalise(category)
        label = self._category_names.setdefault(key, category.strip())

        # One batched call for the whole document instead of one call per chunk.
        vectors = self._doc_embeddings.embed_documents(pieces)

        start = len(self.chunks)
        for index, (piece, vector) in enumerate(zip(pieces, vectors), start=1):
            self.chunks.append(
                Chunk(
                    chunk_id=f"{source}#chunk-{index}",
                    source=source,
                    category=label,
                    text=piece,
                    embedding=vector,
                )
            )
        return len(self.chunks) - start

    def clear(self) -> None:
        self.chunks.clear()
        self._category_names.clear()

    @property
    def sources(self) -> List[str]:
        """Every distinct document name currently stored, in insertion order."""
        seen: List[str] = []
        for chunk in self.chunks:
            if chunk.source not in seen:
                seen.append(chunk.source)
        return seen

    @property
    def categories(self) -> List[str]:
        """Every distinct category, spelled the way it was first ingested."""
        seen: List[str] = []
        for chunk in self.chunks:
            if chunk.category not in seen:
                seen.append(chunk.category)
        return seen

    def resolve_category(self, category: str) -> Optional[str]:
        """Canonical spelling of a requested category, or ``None`` if unknown.

        Callers use the ``None`` to say so politely instead of searching
        everything, which would silently ignore the filter the user asked for.
        """
        label = self._category_names.get(normalise(category))
        # A category whose only document was cleared away is no longer usable.
        return label if label in self.categories else None

    def chunk_counts(self) -> Dict[str, Dict[str, object]]:
        """Per category: how many chunks, and which documents they came from.

        This is what ``GET /sources`` reports.
        """
        summary: Dict[str, Dict[str, object]] = {}
        for chunk in self.chunks:
            entry = summary.setdefault(
                chunk.category, {"chunks": 0, "sources": []}
            )
            entry["chunks"] = int(entry["chunks"]) + 1
            sources: List[str] = entry["sources"]  # type: ignore[assignment]
            if chunk.source not in sources:
                sources.append(chunk.source)
        return summary

    # -- Requirement B: filter, then retrieve -------------------------------- #
    def search(
        self,
        question: str,
        category: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Return the ``top_k`` closest chunks, best first.

        With a category, only that category's chunks are candidates -- an
        employee asking IT about a password never sees the leave policy, however
        similar the wording happens to be.
        """
        candidates = self.chunks
        if category is not None:
            key = normalise(category)
            candidates = [c for c in self.chunks if normalise(c.category) == key]

        if not candidates:
            return []

        query_vector = self._query_embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in candidates
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
            "You are an internal knowledge-base assistant covering HR, IT and "
            "finance. You answer employees using ONLY the extracts supplied in "
            "the context.\n\n"
            "Rules:\n"
            "1. Use only the retrieved extracts. Never rely on your own knowledge "
            "and never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, amounts, "
            "percentages) rather than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
            "4. A question about the world outside these documents always gets "
            "that same sentence. So does a question the extracts you were given "
            "cannot answer, even if you suspect another department's documents "
            "could -- the search was deliberately restricted.\n"
            "5. In used_extracts, list only the extract numbers you actually drew "
            "on. Retrieval returns the closest three extracts whether or not they "
            "are relevant, so an extract you ignored must not be listed.\n"
            "Answer in two or three sentences of plain prose. Do not add a "
            "preamble such as 'Based on the context'.",
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
    """Render the retrieved chunks, labelled with their category and file."""
    return "\n\n".join(
        f"[Extract {rank} -- category: {chunk.category} -- source: {chunk.source}]\n"
        f"{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


@dataclass
class Answer:
    """A grounded answer, what was searched, and the documents behind it."""

    answer: str
    category_searched: str = "all"
    sources_used: List[str] = field(default_factory=list)
    chunks_used: List[Tuple[Chunk, float]] = field(default_factory=list)


def answer_question(
    question: str,
    store: DocumentStore,
    category: Optional[str] = None,
    top_k: int = TOP_K,
) -> Answer:
    """Retrieve within the requested category, then answer from what came back."""
    searched = category or "all"

    results = store.search(question, category=category, top_k=top_k)
    if not results:
        return Answer(answer=FALLBACK, category_searched=searched)

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
        return Answer(answer=text or FALLBACK, category_searched=searched)

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
    return Answer(
        answer=text,
        category_searched=searched,
        sources_used=sources,
        chunks_used=used,
    )
