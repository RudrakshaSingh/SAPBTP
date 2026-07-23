"""Agentic AI course-support service using Google Gemini and FastAPI.

Install:
    pip install -r requirements.txt

Set the Gemini API key in the .env file next to this script:
    GOOGLE_API_KEY=your-key
    GEMINI_MODEL=gemini-2.5-flash

Run:
    python app.py
    (or: uvicorn app:app --reload)

Swagger UI:
    http://localhost:8000/docs

Where things live:
    config.py  API key, model name, shared Gemini client
    data.py    Sample courses and orders
    tools.py   The functions Gemini is allowed to call
    agent.py   System instruction and the Gemini call
    models.py  Request/response schemas
    app.py     The API endpoints (this file)
    tests.py   Mock tests that do not use Gemini quota
"""

from typing import Callable

from fastapi import Depends, FastAPI, HTTPException

from agent import run_agent
from config import MODEL_NAME
from models import ChatRequest, ChatResponse, HealthResponse

app = FastAPI(
    title="Gemini Course Support Agent API",
    description="A simple tool-using agent built with Google Gemini and FastAPI.",
    version="1.0.0",
)


def get_agent_service() -> Callable[[str], str]:
    """FastAPI dependency that supplies the Gemini agent function."""
    return run_agent


@app.get("/", tags=["General"])
def home() -> dict:
    """Return basic API information."""
    return {
        "message": "Gemini Course Support Agent API",
        "documentation": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["General"],
)
def health() -> HealthResponse:
    """Return API health information without calling Gemini."""
    return HealthResponse(status="healthy", model=MODEL_NAME)


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Agent"],
)
def chat(
    request: ChatRequest,
    agent_service: Callable[[str], str] = Depends(get_agent_service),
) -> ChatResponse:
    """Send a message to the Gemini tool-using agent."""
    try:
        answer = agent_service(request.message)
        return ChatResponse(answer=answer, model=MODEL_NAME)
    except Exception as exc:
        # Log the full exception internally in a production application.
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable.",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
