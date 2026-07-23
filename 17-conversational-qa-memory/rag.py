"""
THE THINKING HALF -- STEPS 6 and 7

Two jobs, one per requirement from the problem statement:

    B) Turn a vague follow-up into a standalone question  -> STEP 6
    C) Answer that question from the documents, grounded   -> STEP 7
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config import CHAT_MODEL, FALLBACK, MAX_HISTORY_MESSAGES, TOP_K
from doc_qa import Chunk, DocumentStore
from sessions import Message


# =============================================================================
# STEP 6 -- REQUIREMENT B: REWRITE THE FOLLOW-UP INTO A STANDALONE QUESTION
# =============================================================================
# "And can I carry them over?" means nothing to a search engine -- it does not
# know what "them" is. Retrieval only works on self-contained questions, so
# before searching we show Gemini the conversation so far and ask it to fill in
# the blanks: "Can annual leave be carried over?".
#
# It is told NOT to answer, only to rewrite. temperature=0 keeps it faithful --
# we do not want it inventing detail the user never said.
# =============================================================================

CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You rewrite a follow-up question so it can be understood on its "
            "own, without the chat history.\n\n"
            "Rules:\n"
            "1. Replace vague references like 'it', 'them' or 'that' with what "
            "they actually refer to in the conversation.\n"
            "2. Do NOT answer the question. Return only the rewritten question.\n"
            "3. Do NOT add any detail that the conversation does not support.\n"
            "4. If the question already stands on its own, return it unchanged.",
        ),
        (
            "human",
            "Conversation so far:\n"
            "----------------\n"
            "{history}\n"
            "----------------\n\n"
            "Follow-up question: {question}\n\n"
            "Standalone question:",
        ),
    ]
)


def format_history(messages: List[Message]) -> str:
    """The last few turns as plain 'User:' / 'Assistant:' lines for the prompt."""
    recent = messages[-MAX_HISTORY_MESSAGES:]
    return "\n".join(
        f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}"
        for m in recent
    )


def rewrite_follow_up(question: str, history: List[Message]) -> str:
    """Make a follow-up self-contained. The first question has no history, so it
    is already standalone and returned untouched -- and we save an LLM call."""
    if not history:
        return question

    model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    chain = CONDENSE_PROMPT | model | StrOutputParser()
    standalone = chain.invoke(
        {"history": format_history(history), "question": question}
    ).strip()

    # If the rewrite came back empty for any reason, fall back to the original.
    return standalone or question


# =============================================================================
# STEP 7 -- REQUIREMENT C: ANSWER FROM THE DOCUMENTS, AND CITE THEM
# =============================================================================
# Retrieval found the right paragraphs; this prompt stops the model adding its
# own "knowledge" on top. It answers ONLY from the extracts, or says it cannot.
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
            "2. Quote the actual figures from the extracts (days, weeks) rather "
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


def answer_question(
    question: str,
    store: DocumentStore,
    top_k: int = TOP_K,
) -> Tuple[str, List[str]]:
    """Return (answer, sources_used) for one already-standalone question."""
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

    # If the answer wasn't in the documents, cite nothing -- listing sources next
    # to the fallback sentence would imply we found an answer in them.
    if not answer or answer == FALLBACK:
        return answer or FALLBACK, []

    sources = list(dict.fromkeys(chunk.source for chunk, _score in results))
    return answer, sources
