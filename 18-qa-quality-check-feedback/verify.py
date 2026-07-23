"""
STEP 6 -- REQUIREMENT A: IS THE ANSWER ACTUALLY SUPPORTED BY THE DOCUMENTS?

A grounded prompt usually behaves, but "usually" is not good enough to put in
front of real employees. So after generating an answer we check it, and the
check has to use the RETRIEVED DOCUMENTS, not the model's opinion of itself.

Two signals, both drawn from the retrieval, never from outside knowledge:

  * supported  -- a strict fact-checker LLM sees ONLY the retrieved extracts and
                  the answer, and rules whether every claim is backed by them.
  * confidence -- the best retrieval similarity score: how close the question is
                  to anything we actually store. A deterministic number, not a
                  guess. "stock price today" matches nothing, so it scores low.
"""

from __future__ import annotations

from typing import List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config import CHAT_MODEL, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, FALLBACK
from doc_qa import Chunk
from rag import format_context


# -----------------------------------------------------------------------------
# The fact-checker. It is deliberately blunt: judge only from the extracts, and
# answer in one word so we can read the verdict without parsing prose.
# -----------------------------------------------------------------------------

CHECK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a strict fact-checker for an HR assistant. You are given "
            "some extracts from HR documents and a proposed answer.\n\n"
            "Decide whether EVERY factual claim in the answer is directly "
            "supported by the extracts. Judge only from the extracts -- never "
            "use outside knowledge.\n\n"
            "Reply with exactly one word: SUPPORTED or NOT_SUPPORTED.",
        ),
        (
            "human",
            "Extracts:\n"
            "----------------\n"
            "{context}\n"
            "----------------\n\n"
            "Proposed answer: {answer}",
        ),
    ]
)


def _confidence_from_score(score: float) -> str:
    """Turn the best similarity score into high / medium / low."""
    if score >= CONFIDENCE_HIGH:
        return "high"
    if score >= CONFIDENCE_MEDIUM:
        return "medium"
    return "low"


def check_support(
    answer: str,
    results: List[Tuple[Chunk, float]],
) -> Tuple[bool, str]:
    """Return (supported, confidence) for one answer against its retrieval."""
    # Nothing retrieved, or the model already refused -> nothing to support.
    if not results or answer.strip() == FALLBACK:
        return False, "low"

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = CHECK_PROMPT | model | StrOutputParser()
    verdict = chain.invoke(
        {"context": format_context(results), "answer": answer}
    ).strip().upper()

    supported = verdict.startswith("SUPPORTED")
    if not supported:
        # Not grounded -> we do not trust it, whatever the retrieval score said.
        return False, "low"

    # Grounded: how confident depends on how close the question sat to the docs.
    best_score = results[0][1]
    return True, _confidence_from_score(best_score)
