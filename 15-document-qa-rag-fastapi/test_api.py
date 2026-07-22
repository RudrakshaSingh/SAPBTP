"""Walk the evaluation checklist against the real API.

    python test_api.py

Runs the app in-process with FastAPI's TestClient -- no server needed, but the
Gemini calls are real, so a valid GOOGLE_API_KEY must be in .env.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import app

# The last one is deliberately outside the documents.
QUESTIONS = [
    "How many annual leave days do I get?",
    "What is the work-from-home policy?",
    "Can I carry forward unused leave?",
    "What is the notice period for resignation?",
    "How many sick leaves are allowed per year?",
    "Who is the current Prime Minister?",
]

EXTRA_DOCUMENT = {
    "source": "travel_policy.txt",
    "text": (
        "Business Travel\n\n"
        "Domestic travel is booked through the travel desk at least 7 days in "
        "advance. Employees at grade M3 and above travel by air; all other "
        "grades travel by train in AC 2-tier.\n\n"
        "Per Diem\n\n"
        "The domestic per diem is 1,800 INR per day for metro cities and 1,200 "
        "INR per day elsewhere. Receipts are not required for per diem, but "
        "hotel bills must be uploaded within 10 days of returning."
    ),
}


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main() -> None:
    with TestClient(app) as client:
        banner("GET /health")
        response = client.get("/health")
        print(response.status_code, response.json())

        banner("POST /ingest -- add one more document at runtime")
        response = client.post("/ingest", json={"documents": [EXTRA_DOCUMENT]})
        print(response.status_code, response.json())

        banner("POST /ask")
        for question in QUESTIONS:
            payload = client.post("/ask", json={"question": question}).json()
            print(f"\nQ: {question}")
            print(f"A: {payload['answer']}")
            print(f"   sources_used: {payload['sources_used']}")

        banner("POST /ask -- the newly ingested document")
        payload = client.post(
            "/ask", json={"question": "What is the per diem for metro cities?"}
        ).json()
        print(f"\nA: {payload['answer']}")
        print(f"   sources_used: {payload['sources_used']}")


if __name__ == "__main__":
    main()
