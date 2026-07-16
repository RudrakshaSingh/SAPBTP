"""Pydantic models for structured recommendation output.

Bonus requirement #3: the result is returned as a Pydantic model.
Bonus requirement #4: source metadata is attached to each recommendation.
"""

from typing import List, Literal

from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    """Decides how to handle an incoming message.

    ``recommend`` -> the user wants course guidance, so run the RAG
    recommendation. ``general`` -> greetings, catalog listing, questions about a
    course, or anything else; answer conversationally via ``reply``.
    """

    intent: Literal["recommend", "general"] = Field(
        ...,
        description=(
            "'recommend' when the user asks which course(s) to take, what to "
            "learn, a learning path, or describes their background seeking "
            "guidance. 'general' for greetings, small talk, listing/browsing "
            "the catalog, questions about a specific course, or anything else."
        ),
    )
    reply: str = Field(
        default="",
        description=(
            "A helpful, friendly reply. Fill this ONLY when intent is "
            "'general'. Leave empty when intent is 'recommend'."
        ),
    )


class SourceMetadata(BaseModel):
    """Provenance for a single recommended course (bonus #4)."""

    course_id: str = Field(..., description="Unique course identifier, e.g. COURSE_001")
    course_name: str = Field(..., description="Human readable course name")
    experience_level: str = Field(..., description="Target experience level")
    duration: str = Field(..., description="Course duration, e.g. '6 hours'")
    source: str = Field(
        ...,
        description="Where this record came from, e.g. 'courses.py::COURSE_001'",
    )


class RecommendationResponse(BaseModel):
    """The structured output the LLM is asked to produce."""

    recommended_courses: List[str] = Field(
        ...,
        description="Course ids (e.g. COURSE_001) recommended for the learner, best first.",
    )
    reason: str = Field(
        ...,
        description="Concise explanation of why these courses fit the learner's profile.",
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisites the learner should have before starting.",
    )
    learning_sequence: List[str] = Field(
        default_factory=list,
        description="Recommended ordered path (course ids) from first to last.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the recommendation, from 0.0 to 1.0.",
    )


class FinalRecommendation(RecommendationResponse):
    """The enriched response returned to the caller.

    Extends the LLM output with source metadata and the total learning
    hours computed by the custom tool (bonus #1 and #4).
    """

    sources: List[SourceMetadata] = Field(default_factory=list)
    total_learning_hours: int = Field(
        default=0,
        description="Sum of durations for all recommended courses.",
    )
