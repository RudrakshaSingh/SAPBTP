"""Walk the evaluation checklist against the real API.

    python test_api.py

Runs the app in-process with FastAPI's TestClient -- no server needed, but the
Gemini calls are real, so a valid GOOGLE_API_KEY must be in .env.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import app

# (category, question). None means "no filter -- search everything".
QUESTIONS = [
    ("IT", "My VPN keeps disconnecting, what should I do?"),
    ("Finance", "What is the daily meal allowance on business trips?"),
    (None, "What are the working hours?"),
    ("IT", "How do I reset my email password?"),
    ("Finance", "What is the travel reimbursement limit?"),
    ("HR", "How many casual leaves do I have?"),
    # The filter must win over similarity: the leave policy is the closest
    # match in the corpus, but the search never leaves IT.
    ("IT", "How many casual leaves do I have?"),
    # Same question, no filter -- now HR is reachable.
    (None, "How many casual leaves do I have?"),
    # Nothing in any document answers this one.
    (None, "Who is the current Prime Minister?"),
]

EXTRA_DOCUMENT = {
    "source": "legal_nda_faq.txt",
    "category": "Legal",
    "text": (
        "Non-Disclosure Agreements\n\n"
        "Every NDA is reviewed by the legal team before signature and takes up "
        "to 5 working days. Mutual NDAs use the standard template and need no "
        "review when unchanged.\n\n"
        "Retention\n\n"
        "Signed contracts are retained for 7 years after expiry in the contract "
        "repository. Business teams must not keep private copies."
    ),
}


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def show(client: TestClient, question: str, category: str | None) -> None:
    payload = {"question": question}
    if category is not None:
        payload["category"] = category

    body = client.post("/ask", json=payload).json()
    print(f"\nQ: {question}   (category: {category or 'all'})")
    print(f"A: {body['answer']}")
    print(f"   category_searched: {body['category_searched']}")
    print(f"   sources_used: {body['sources_used']}")


def main() -> None:
    with TestClient(app) as client:
        banner("GET /health")
        response = client.get("/health")
        print(response.status_code, response.json())

        banner("GET /sources -- categories and chunk counts")
        print(client.get("/sources").json())

        banner("POST /ask -- filtered and unfiltered")
        for category, question in QUESTIONS:
            show(client, question, category)

        banner("POST /ask -- a category nobody has ingested")
        show(client, "How do I claim relocation costs?", "Marketing")

        banner("POST /ingest -- add a whole new category at runtime")
        response = client.post("/ingest", json={"documents": [EXTRA_DOCUMENT]})
        print(response.status_code, response.json())

        banner("POST /ask -- the newly ingested category")
        show(client, "How long does an NDA review take?", "legal")

        banner("GET /sources -- after ingest")
        print(client.get("/sources").json())


if __name__ == "__main__":
    main()
