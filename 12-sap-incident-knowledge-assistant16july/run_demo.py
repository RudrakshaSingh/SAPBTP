"""Run the full SAP Incident Knowledge Assistant demo.

Covers Task 7 (semantic retrieval), Task 8 (metadata filtering) and every
mandatory test question from section 7 of the problem statement.

Run:
    python create_dataset.py     # once, to produce sap_incidents.xlsx
    python run_demo.py
"""

from __future__ import annotations

from incident_rag import (
    answer_question,
    ask_incident_rag,
    build_assistant,
    print_retrieval,
    retrieve,
)

# Task 7 -- wording deliberately differs from the Excel text.
RETRIEVAL_TESTS = [
    "Which incident was related to HANA memory exhaustion?",
    "Find incidents involving SAP BTP connectivity problems.",
    "Which issue was caused by an incorrect pricing procedure?",
    "Show incidents related to employee integration failures.",
]

# Task 8 -- semantic search narrowed by structured fields.
FILTER_TESTS = [
    ("Show the most critical incidents.", {"priority": "P1"}),
    ("Database problems.", {"sap_module": "SAP HANA"}),
    ("Access and connection issues.", {"sap_module": "SAP BTP", "owner_team": "BTP Platform Team"}),
]

# Section 7 -- mandatory test questions.
MANDATORY_QUESTIONS = [
    # Direct factual
    ("What was the resolution for incident INC-1004?", {}),
    ("Which team resolved the employee replication issue?", {}),
    # Semantic
    ("Has there been an issue where a cloud application could not connect to an SAP backend?", {}),
    ("Find a previous incident involving database memory problems.", {}),
    # Comparison
    ("Which P1 incident took the longest time to resolve?", {}),
    ("Compare the two SAP HANA P1 incidents.", {}),
    # Filter-based
    ("Show only P1 SAP BTP incidents.", {"sap_module": "SAP BTP", "priority": "P1"}),
    (
        "Find SAP MM incidents handled by the Procure-to-Pay Support team.",
        {"sap_module": "SAP MM", "owner_team": "Procure-to-Pay Support"},
    ),
    # Recommendation-style
    (
        "A user reports that a BTP application cannot access the backend because "
        "authentication is failing. Which previous incident is most similar, and "
        "what resolution should the support team investigate?",
        {},
    ),
    # Unsupported -- must refuse rather than invent
    ("What is the annual revenue of the company?", {}),
]

# Section 11 -- questions vector retrieval alone cannot answer correctly.
ANALYTICAL_QUESTIONS = [
    "What is the average resolution time for SAP HANA incidents?",
    "How many P1 incidents were reported?",
    "Which module has the highest average resolution time?",
]

# Section 8 -- the worked example from the problem statement.
EXPECTED_OUTPUT_QUESTION = "Which P1 SAP HANA incident took the longest to resolve?"


def main() -> None:
    store, df = build_assistant()

    print("\n" + "=" * 70)
    print("TASK 7 -- SEMANTIC RETRIEVAL")
    print("=" * 70)
    for question in RETRIEVAL_TESTS:
        print_retrieval(question, retrieve(store, question, top_k=3))

    print("\n" + "=" * 70)
    print("TASK 8 -- METADATA FILTERING")
    print("=" * 70)
    for question, filters in FILTER_TESTS:
        print(f"\nFilters: {filters}")
        print_retrieval(question, retrieve(store, question, top_k=3, **filters), show_text=False)

    print("\n" + "=" * 70)
    print("MANDATORY TEST QUESTIONS")
    print("=" * 70)
    for question, filters in MANDATORY_QUESTIONS:
        answer_question(question, store, df, **filters).display()

    print("\n" + "=" * 70)
    print("SECTION 11 -- ANALYTICAL QUESTIONS ROUTED TO PANDAS")
    print("=" * 70)
    for question in ANALYTICAL_QUESTIONS:
        answer_question(question, store, df).display()

    print("\n" + "=" * 70)
    print("SECTION 8 -- EXPECTED FINAL OUTPUT")
    print("=" * 70)
    ask_incident_rag(
        EXPECTED_OUTPUT_QUESTION, store, sap_module="SAP HANA", priority="P1"
    ).display()


if __name__ == "__main__":
    main()
