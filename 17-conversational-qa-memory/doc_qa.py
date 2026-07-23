"""
THE RETRIEVAL HALF -- STEPS 3 and 4

This is the same retrieval engine as Hands-on 2, with the category filter taken
out: this project has a single HR knowledge base, so there is nothing to filter
by. Its whole job is to find the document pieces closest to a question.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

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


# =============================================================================
# STEP 4 -- STORE THE CHUNKS AND SEARCH THEM
# =============================================================================
# The constraint says no external database, so the "database" is a Python list.
# With a handful of documents one loop is genuinely faster than building an
# index would be.
# =============================================================================

@dataclass
class Chunk:
    """One piece of one document, tagged with where it came from."""

    source: str             # file name, shown to the user as the citation
    text: str               # the actual words
    embedding: List[float]  # the numbers representing this text's meaning


class DocumentStore:
    """Embedded chunks in memory: score every chunk against the question."""

    def __init__(self) -> None:
        self.chunks: List[Chunk] = []
        self.embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    def add_document(self, text: str, source: str) -> int:
        """Chunk it, embed it, store it. Returns how many chunks were created."""
        pieces = chunk_text(text)
        if not pieces:
            return 0

        # One batched call for the whole document, not one call per chunk.
        vectors = self.embeddings.embed_documents(pieces)

        for piece, vector in zip(pieces, vectors):
            self.chunks.append(Chunk(source=source, text=piece, embedding=vector))
        return len(pieces)

    @property
    def sources(self) -> List[str]:
        """Every distinct document name, in the order they were added."""
        return list(dict.fromkeys(chunk.source for chunk in self.chunks))

    def search(self, question: str, top_k: int = TOP_K) -> List[Tuple[Chunk, float]]:
        """Return the top_k closest chunks as (chunk, score) pairs, best first."""
        if not self.chunks:
            return []

        query_vector = self.embeddings.embed_query(question)
        scored = [
            (chunk, cosine_similarity(query_vector, chunk.embedding))
            for chunk in self.chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]
