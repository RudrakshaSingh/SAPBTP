"""
STEP 8 -- THE SHAPES OF THE API (what goes in, what comes out)

Every class here is a Pydantic model describing valid JSON. FastAPI uses them
to reject bad input with a 422, guarantee our replies are valid JSON, and build
the interactive docs at /docs -- all for free.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator

from config import TOP_K


class DocumentIn(BaseModel):
    source: str = Field(description="File name shown in sources_used, e.g. hr_policy.txt")
    text: str = Field(description="The full plain text of the document")

    # min_length=1 would still let "   " through, and a whitespace-only document
    # embeds into nothing useful. Rejecting it here beats storing an empty chunk.
    @field_validator("source", "text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class IngestedDocument(BaseModel):
    source: str
    chunks: int


class IngestResponse(BaseModel):
    status: str
    ingested: List[IngestedDocument]
    total_chunks: int


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=TOP_K, ge=1, le=10, description="How many extracts to retrieve")

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()


class AskResponse(BaseModel):
    answer: str
    sources_used: List[str]
