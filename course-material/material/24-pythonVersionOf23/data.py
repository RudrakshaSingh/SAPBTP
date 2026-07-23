"""Sample business data the agent's tools read from."""

COURSES = [
    {
        "course_id": "C101",
        "name": "Python for Generative AI",
        "category": "Python",
        "level": "Beginner",
        "price_inr": 5000,
    },
    {
        "course_id": "C102",
        "name": "Agentic AI with LangGraph",
        "category": "Agentic AI",
        "level": "Intermediate",
        "price_inr": 8000,
    },
    {
        "course_id": "C103",
        "name": "SAP Business AI Fundamentals",
        "category": "SAP Business AI",
        "level": "Beginner",
        "price_inr": 10000,
    },
    {
        "course_id": "C104",
        "name": "FastAPI for AI Applications",
        "category": "API Development",
        "level": "Intermediate",
        "price_inr": 6000,
    },
]

ORDERS = {
    "ORD-1001": {
        "status": "confirmed",
        "course_id": "C103",
        "learner": "Amit",
    },
    "ORD-1002": {
        "status": "payment_pending",
        "course_id": "C102",
        "learner": "Neha",
    },
    "ORD-1003": {
        "status": "completed",
        "course_id": "C101",
        "learner": "Rahul",
    },
}
