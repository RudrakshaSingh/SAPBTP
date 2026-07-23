"""
STEP 8 -- THE SHAPES OF THE API (what goes in, what comes out)

Every class here is a Pydantic model describing valid JSON. FastAPI uses them
to reject bad input with a 422, guarantee our replies are valid JSON, and
build the interactive docs at /docs -- all for free.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    source: str = Field(min_length=1, description="File name, e.g. it_faq.txt")
    category: str = Field(min_length=1, description="Knowledge area, e.g. HR")
    text: str = Field(min_length=1, description="The full text of the document")


class IngestRequest(BaseModel):
    documents: List[DocumentIn] = Field(min_length=1)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    category: Optional[str] = Field(
        default=None,
        description="Restrict the search to one category. Omit to search all.",
    )


class AskResponse(BaseModel):
    answer: str
    category_searched: str
    sources_used: List[str]
