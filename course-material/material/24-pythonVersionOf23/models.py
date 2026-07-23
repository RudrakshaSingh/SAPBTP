"""Request and response schemas for the API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Input accepted by POST /chat."""

    message: str = Field(
        min_length=2,
        max_length=1000,
        examples=[
            "What is the price of the SAP Business AI course "
            "after a 10% discount?"
        ],
    )


class ChatResponse(BaseModel):
    """Output returned by POST /chat."""

    answer: str
    model: str


class HealthResponse(BaseModel):
    """Output returned by GET /health."""

    status: str
    model: str
