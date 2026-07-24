"""
THE GENERATION HALF -- STEPS 5 to 7

Retrieval (doc_qa.py) found the right paragraphs. This module turns them into
an answer and covers the last requirement from the problem statement:

    C) Answer using ONLY the retrieved text, and say which sources it used
       -> STEP 5 (the prompt), STEP 6 (the citation), STEP 7 (the pipeline)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config import CHAT_MODEL, FALLBACK, TOP_K
from doc_qa import Chunk, DocumentStore


# =============================================================================
# STEP 5 -- THE PROMPT THAT KEEPS GEMINI HONEST
# =============================================================================
# Retrieval found the right paragraphs; this stops the model adding its own
# "knowledge" on top. temperature=0 means "be as predictable as possible" --
# right for quoting a policy document, wrong for creative writing.
#
# Note: the flash-lite models use fixed sampling and print a UserWarning saying
# temperature was ignored. That is harmless -- they are already near
# deterministic. The setting is kept so the code still behaves if you switch to
# a model that does honour it.
# =============================================================================

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
    """Lay out the retrieved chunks as numbered, labelled extracts."""
    return "\n\n".join(
        f"[Extract {rank} -- source: {chunk.source}]\n{chunk.text}"
        for rank, (chunk, _score) in enumerate(results, start=1)
    )


# =============================================================================
# STEP 6 -- REQUIREMENT C: MAKE THE MODEL NAME THE EXTRACTS IT USED
# =============================================================================
# Retrieval always hands over three extracts, relevant or not. Citing all three
# would credit documents the answer never touched, so instead of a plain string
# we ask Gemini for a small structured object: the prose answer, PLUS the
# extract numbers behind it. `with_structured_output` makes that a schema the
# model must fill in rather than a formatting request it might ignore.
# =============================================================================

class GroundedAnswer(BaseModel):
    """What the model must return: the answer, and which extracts produced it."""

    answer: str = Field(description="The answer, or the exact fallback sentence.")
    used_extracts: List[int] = Field(
        description=(
            "The extract numbers that actually support the answer, e.g. [1, 3]. "
            "Leave empty when answering with the fallback sentence."
        )
    )


@dataclass
class Answer:
    """A grounded answer plus the documents behind it."""

    answer: str
    sources_used: List[str] = field(default_factory=list)
    # The (chunk, score) pairs the answer actually leaned on. Nothing in the API
    # surfaces these yet -- they are what you would return to cite the exact
    # clause rather than just the file name.
    chunks_used: List[Tuple[Chunk, float]] = field(default_factory=list)


# =============================================================================
# STEP 7 -- THE FULL PIPELINE FOR ONE QUESTION
# =============================================================================
# search -> build the prompt -> ask Gemini -> map the extract numbers it cited
# back to document names.
# =============================================================================

def answer_question(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Answer:
    """Retrieve, then generate an answer grounded in what was retrieved."""
    results = store.search(question, top_k=top_k)

    # Nothing stored at all -- don't call the AI.
    if not results:
        return Answer(answer=FALLBACK)

    # The `|` pipe is LangChain for "feed this into that".
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

    # The numbers are 1-based positions in `results`. Anything outside that
    # range is a citation the model made up, so it is dropped rather than
    # trusted. dict.fromkeys de-duplicates while keeping the model's order.
    used = [
        results[number - 1]
        for number in dict.fromkeys(result.used_extracts)
        if 1 <= number <= len(results)
    ]

    sources = list(dict.fromkeys(chunk.source for chunk, _score in used))
    return Answer(answer=text, sources_used=sources, chunks_used=used)
