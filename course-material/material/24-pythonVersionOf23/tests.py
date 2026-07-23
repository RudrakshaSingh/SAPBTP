"""Optional local checks.

Run the mock tests (no Gemini quota used):
    python tests.py

Run the live demo against Gemini (uses quota):
    python tests.py live
"""

import sys

from app import app, get_agent_service
from agent import run_agent


def run_mock_api_tests() -> None:
    """Test FastAPI routing and validation without consuming Gemini quota."""
    from fastapi.testclient import TestClient

    def fake_agent(message: str) -> str:
        return f"Mock agent received: {message}"

    app.dependency_overrides[get_agent_service] = lambda: fake_agent

    try:
        test_client = TestClient(app)

        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        chat_response = test_client.post(
            "/chat",
            json={"message": "Show me an SAP AI course"},
        )
        assert chat_response.status_code == 200
        assert "Mock agent received" in chat_response.json()["answer"]

        invalid_response = test_client.post(
            "/chat",
            json={"message": ""},
        )
        assert invalid_response.status_code == 422

        print("All mock FastAPI tests passed.")
    finally:
        app.dependency_overrides.clear()


def run_direct_agent_demo() -> None:
    """Call Gemini with three sample questions. This consumes Gemini quota."""
    sample_questions = [
        "Which beginner SAP course is available?",
        "What will course C103 cost after a 15 percent discount?",
        "What is the status of order ORD-1002?",
    ]

    for question in sample_questions:
        print("\nUSER:", question)
        print("AGENT:", run_agent(question))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        run_direct_agent_demo()
    else:
        run_mock_api_tests()
