"""
THE GENERATION HALF -- STEPS 6 and 7

Retrieval (doc_qa.py) found the right paragraphs. This module turns them into
an answer and covers the last requirement from the problem statement:

    C) The answer says which source(s) it used  -> STEP 7
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config import CHAT_MODEL, FALLBACK, TOP_K
from doc_qa import Chunk, DocumentStore


# =============================================================================
# STEP 6 -- THE PROMPT THAT KEEPS GEMINI HONEST
# =============================================================================
# Retrieval found the right paragraphs; this stops the model adding its own
# "knowledge" on top. temperature=0 means "be as predictable as possible" --
# right for quoting a policy document, wrong for creative writing.
#
# Note: the flash-lite models use fixed sampling and print a UserWarning saying
# temperature was ignored. That is harmless -- they are already near
# deterministic. The setting is kept so the code still behaves if you switch
# to a model that does honour it.
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
    """Lay out the retrieved chunks as numbered, labelled extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- category: {chunk.category} -- source: {chunk.source}]\n"
        f"{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


# =============================================================================
# STEP 7 -- REQUIREMENT C: ANSWER, AND SAY WHERE IT CAME FROM
# =============================================================================
# The full pipeline for one question: search -> build prompt -> ask Gemini ->
# report the documents behind the answer.
# =============================================================================

def answer_question(
    question: str,
    store: DocumentStore,
    category: Optional[str] = None,
    top_k: int = TOP_K,
) -> Tuple[str, List[str]]:
    """Return (answer, sources_used)."""
    results = store.search(question, category=category, top_k=top_k)

    # Nothing stored, or nothing in that category -- don't call the AI at all.
    if not results:
        return FALLBACK, []

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)

    # The `|` pipe is LangChain for "feed this into that". StrOutputParser at
    # the end turns the model's reply into a plain string -- without it some
    # Gemini models hand back a list of content blocks instead of text.
    chain = RAG_PROMPT | model | StrOutputParser()

    answer = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
        }
    ).strip()

    # If the answer wasn't in the documents, cite nothing. Listing sources next
    # to the fallback sentence would imply we found an answer in them.
    if not answer or answer == FALLBACK:
        return answer or FALLBACK, []

    # Otherwise the sources are the documents the retrieved chunks came from,
    # de-duplicated and kept in rank order.
    sources = list(dict.fromkeys(chunk.source for chunk, _score in results))
    return answer, sources
