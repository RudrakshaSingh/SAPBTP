"""
STEP 8 -- THE SHAPES OF THE API (what goes in, what comes out)

Every class here is a Pydantic model describing valid JSON. FastAPI uses them
to reject bad input with a 422, guarantee our replies are valid JSON, and build
the interactive docs at /docs -- all for free.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class NewSessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, description="From POST /session/new")
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources_used: List[str]


class MessageOut(BaseModel):
    role: str      # "user" or "assistant"
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageOut]
