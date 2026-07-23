"""
THE ANSWER HALF -- STEP 5

Retrieval (doc_qa.py) found the right paragraphs. This module turns them into a
grounded answer. The quality check that decides whether to trust it lives next
door in verify.py (STEP 6).

generate_answer returns the answer AND the retrieved (chunk, score) results, so
the caller can both cite the sources and hand the same chunks to the checker --
the check must judge against exactly what the answer was built from.
"""

from __future__ import annotations

from typing import List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config import CHAT_MODEL, FALLBACK, TOP_K
from doc_qa import Chunk, DocumentStore


# =============================================================================
# STEP 5 -- THE PROMPT THAT KEEPS GEMINI HONEST
# =============================================================================
# Retrieval found the right paragraphs; this stops the model adding its own
# "knowledge" on top. temperature=0 means "be as predictable as possible" --
# right for quoting a policy document, wrong for creative writing.
# =============================================================================

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an internal HR assistant. Answer employees using ONLY the "
            "extracts supplied below.\n\n"
            "Rules:\n"
            "1. Use only the extracts. Never rely on your own knowledge and "
            "never invent a number, a date or a rule.\n"
            "2. Quote the actual figures from the extracts (days, months) rather "
            "than paraphrasing them loosely.\n"
            "3. If the extracts do not contain the answer, reply with exactly "
            "this sentence and nothing else:\n"
            "   {fallback}\n"
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
    """Lay out the retrieved chunks as numbered, labelled extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- source: {chunk.source}]\n{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


def generate_answer(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Tuple[str, List[Tuple[Chunk, float]]]:
    """Return (answer, results). results is the (chunk, score) list retrieved."""
    results = store.search(question, top_k=top_k)

    # Nothing stored at all -- don't call the AI.
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

    return (answer or FALLBACK), results
