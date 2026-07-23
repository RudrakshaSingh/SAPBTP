"""
STEP 8 -- THE SHAPES OF THE API (what goes in, what comes out)

Every class here is a Pydantic model describing valid JSON. FastAPI uses them
to reject bad input with a 422, guarantee our replies are valid JSON, and build
the interactive docs at /docs -- all for free.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    source: str = Field(min_length=1, description="File name, e.g. hr_policy.txt")
    text: str = Field(min_length=1, description="The full text of the document")


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class AskResponse(BaseModel):
    answer: str
    supported_by_documents: bool     # is the answer backed by the retrieved docs?
    confidence: str                  # "high" / "medium" / "low"
    sources_used: List[str]


class FeedbackRequest(BaseModel):
    question: str = Field(min_length=1)
    helpful: bool                    # thumbs up (true) or thumbs down (false)


class FeedbackSummary(BaseModel):
    total: int
    helpful: int
    not_helpful: int
