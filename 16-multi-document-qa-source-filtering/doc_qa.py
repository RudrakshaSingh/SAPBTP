"""
THE RETRIEVAL HALF -- STEPS 3 to 5

Covers two of the three requirements from the problem statement:

    A) Every chunk remembers its category and source name  -> STEP 4
    B) Filter by category BEFORE searching                 -> STEP 5

Requirement C (say which sources were used) lives in rag.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, EMBED_MODEL, TOP_K


# =============================================================================
# STEP 3 -- CHUNKING AND SIMILARITY (the two small helpers)
# =============================================================================
# chunk_text  : cuts a document into pieces, preferring paragraph breaks over
#               line breaks over sentence ends, so a chunk rarely starts
#               mid-sentence.
#
# cosine_similarity : an embedding is a list of numbers representing meaning.
#               Picture each one as an arrow; this measures the ANGLE between
#               two arrows. 1.0 = same direction (same meaning), 0.0 = unrelated.
#               We divide by the arrow lengths so a long document and a short
#               question compare fairly.
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
    """How alike two embeddings are: 1.0 = same meaning, 0.0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def normalise(category: str) -> str:
    """Make category matching forgiving: 'it', ' IT ' and 'It' all match."""
    return category.strip().casefold()


# =============================================================================
# STEP 4 -- REQUIREMENT A: STORE CHUNKS WITH THEIR CATEGORY AND SOURCE
# =============================================================================
# The constraint says no external database, so the "database" is a Python list.
# With a handful of documents one loop is genuinely faster than building an
# index would be.
# =============================================================================

@dataclass
class Chunk:
    """One piece of one document, tagged with where it came from."""

    source: str             # file name, shown to the user as the citation
    category: str           # "HR", "IT", "Finance", ...
    text: str               # the actual words
    embedding: List[float]  # the numbers representing this text's meaning


class DocumentStore:
    """Embedded chunks in memory: filter by category, then score what is left."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    def add_document(self, text: str, source: str, category: str) -> int:
        """Chunk it, embed it, store it. Returns how many chunks were created."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        # One batched call for the whole document, not one call per chunk.
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
        """Every distinct document name, in the order they were added."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    @property
    def categories(self) -> List[str]:
        """Every distinct category, in the order they were added."""
        return list(dict.fromkeys(chunk.category for chunk in self.chunks))

    def resolve_category(self, category: str) -> Optional[str]:
        """Proper spelling of a requested category, or None if we don't have it.

        Returning None lets /ask say "no such category" instead of silently
        searching everything and ignoring the filter the user asked for.
        """
        key = normalise(category)
        for chunk in self.chunks:
            if normalise(chunk.category) == key:
                return chunk.category
        return None

    # ---------------------------------------------------------------- #
    # STEP 5 -- REQUIREMENT B: FILTER FIRST, *THEN* SCORE
    # ---------------------------------------------------------------- #
    # This ordering is the whole point of the project.
    #
    #   FILTER FIRST (what we do):
    #     keep only IT chunks -> score those -> return the best 3 IT chunks.
    #
    #   SCORE FIRST, FILTER AFTER (the tempting mistake):
    #     score all 30 -> take the best 3 -> drop the non-IT ones -> you asked
    #     for 3 and got 1, because HR chunks crowded the top.
    # ---------------------------------------------------------------- #
    def search(
        self,
        question: str,
        category: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> List[Tuple[Chunk, float]]:
        """Return the top_k closest chunks as (chunk, score) pairs, best first."""
        candidates = self.chunks

        # THE FILTER -- applied before any scoring happens.
        if category is not None:
            key = normalise(category)
            candidates = [c for c in self.chunks if normalise(c.category) == key]

        if not candidates:
            return []

        query_vector = self.embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in candidates
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
