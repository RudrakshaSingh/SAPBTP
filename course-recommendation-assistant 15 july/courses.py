"""Sample course catalog for the Course Recommendation Assistant.

Each course document contains: course name, skills taught, experience level,
duration and prerequisites (plus an id and a description used for retrieval).
"""

courses = [
    {
        "course_id": "COURSE_001",
        "course_name": "Introduction to Generative AI for SAP Professionals",
        "skills_taught": [
            "Generative AI fundamentals",
            "Large Language Models",
            "Prompt engineering basics",
            "SAP Business AI overview",
            "Joule overview",
            "AI use cases in SAP",
        ],
        "experience_level": "Beginner",
        "duration": "6 hours",
        "prerequisites": [
            "Basic understanding of SAP applications",
            "No prior AI or machine learning experience required",
        ],
        "course_description": (
            "A beginner-level course for SAP professionals with no previous "
            "AI experience. It introduces Generative AI, Large Language Models, "
            "SAP Business AI, Joule, and SAP AI use cases."
        ),
    },
    {
        "course_id": "COURSE_002",
        "course_name": "Python and LangChain Fundamentals for AI Applications",
        "skills_taught": [
            "Python fundamentals for AI",
            "LangChain basics",
            "Prompt templates",
            "Chains",
            "Large Language Model integration",
            "Gemini API integration",
            "Structured output generation",
        ],
        "experience_level": "Beginner to Intermediate",
        "duration": "10 hours",
        "prerequisites": [
            "Basic programming knowledge",
            "Understanding of Generative AI fundamentals is recommended",
        ],
        "course_description": (
            "Teaches developers how to build Generative AI applications "
            "using Python, LangChain, and Google Gemini."
        ),
    },
    {
        "course_id": "COURSE_003",
        "course_name": "Building RAG Applications with LangChain and Gemini",
        "skills_taught": [
            "Retrieval-Augmented Generation",
            "Document loading",
            "Document chunking",
            "Text embeddings",
            "Vector databases",
            "Semantic search",
            "LangChain retrievers",
            "Gemini integration",
            "Structured RAG responses",
        ],
        "experience_level": "Intermediate",
        "duration": "12 hours",
        "prerequisites": [
            "Basic Python programming",
            "Understanding of Large Language Models",
            "Basic LangChain knowledge",
        ],
        "course_description": (
            "Teaches learners to build complete RAG applications using "
            "LangChain and Google Gemini."
        ),
    },
    {
        "course_id": "COURSE_004",
        "course_name": "SAP Business AI and Generative AI Hub Development",
        "skills_taught": [
            "SAP Business AI architecture",
            "SAP AI Core",
            "Generative AI Hub",
            "Large Language Model access",
            "Prompt engineering on SAP BTP",
            "Python integration with SAP AI Core",
            "Enterprise AI governance",
            "Building custom AI applications on SAP BTP",
        ],
        "experience_level": "Intermediate",
        "duration": "14 hours",
        "prerequisites": [
            "Basic Generative AI knowledge",
            "Basic Python programming",
            "Basic understanding of SAP BTP",
        ],
        "course_description": (
            "Teaches SAP developers how to build enterprise Generative AI "
            "applications using SAP AI Core and Generative AI Hub."
        ),
    },
    {
        "course_id": "COURSE_005",
        "course_name": "Building AI Agents and Custom Joule Agents on SAP BTP",
        "skills_taught": [
            "AI agent fundamentals",
            "Agentic AI architecture",
            "Tool calling",
            "LangChain agents",
            "LangGraph fundamentals",
            "Joule Studio",
            "Custom Joule agents",
            "SAP Integration Suite integration",
            "SAP HANA Cloud Vector Engine",
            "Enterprise AI agent architecture",
        ],
        "experience_level": "Advanced",
        "duration": "18 hours",
        "prerequisites": [
            "Strong understanding of Generative AI",
            "Basic Python programming",
            "Experience with LangChain or similar AI frameworks",
            "Understanding of SAP BTP",
            "Basic knowledge of SAP AI Core and Generative AI Hub",
        ],
        "course_description": (
            "An advanced course for building AI agents and custom Joule agents "
            "using LangChain, LangGraph, Joule Studio, and SAP BTP services."
        ),
    },
]
