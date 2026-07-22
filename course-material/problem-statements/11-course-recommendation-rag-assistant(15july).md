# Problem Statement 11 — Course Recommendation Assistant (RAG)

| | |
|---|---|
| **Project Title** | AI Course Recommendation Assistant using RAG, LangChain and Google Gemini |
| **Domain** | EdTech / Learning & Development |
| **Topic** | Retrieval-Augmented Generation, vector search, Pydantic structured output |
| **Stack** | Python · LangChain · Google Gemini · Gemini Embeddings · FAISS · Pydantic · Streamlit |
| **Implementation** | [`course-recommendation-assistant 15 july/`](../course-recommendation-assistant%2015%20july/) |

---

## 1. Business Scenario

A training provider offers a catalog of SAP + AI courses spanning beginner Generative AI content through advanced agentic AI on SAP BTP. Learners arriving at the catalog do not know where to start. They ask questions in plain language, such as:

> I am an SAP ABAP developer with no AI experience. Which course should I take first to learn SAP Business AI?

A keyword search over course titles cannot answer this — the learner never typed a course name. The answer depends on the learner's **background, experience level, and prerequisites**, all of which are described in free text inside the course records.

Your task is to build a **Retrieval-Augmented Generation** application that reads the course catalog, retrieves the courses most relevant to the learner's question, and asks Gemini to produce a **structured, source-attributed recommendation**.

## 2. Project Objective

Build a RAG application that:

- Turns each course record into a retrievable document.
- Generates embeddings for those documents using Gemini embeddings.
- Stores them in a FAISS vector store.
- Retrieves the most relevant courses for a natural-language question.
- Asks Gemini to return a **validated Pydantic object**, not free text.
- Attaches source metadata so every recommendation is traceable to a catalog record.
- Never invents a course that is not in the catalog.

---

## 3. Course Catalog Dataset

Create a catalog of **5 courses**. Each course record must contain:

| Field | Description |
|---|---|
| `course_id` | Unique identifier, e.g. `COURSE_001` |
| `course_name` | Human-readable course name |
| `skills_taught` | List of skills covered by the course |
| `experience_level` | Beginner, Beginner to Intermediate, Intermediate, Advanced |
| `duration` | Course duration, e.g. `"6 hours"` |
| `prerequisites` | List of things the learner should already know |
| `course_description` | Short paragraph used for retrieval |

### Catalog Contents

| Course ID | Course Name | Level | Duration |
|---|---|---|---|
| COURSE_001 | Introduction to Generative AI for SAP Professionals | Beginner | 6 hours |
| COURSE_002 | Python and LangChain Fundamentals for AI Applications | Beginner to Intermediate | 10 hours |
| COURSE_003 | Building RAG Applications with LangChain and Gemini | Intermediate | 12 hours |
| COURSE_004 | SAP Business AI and Generative AI Hub Development | Intermediate | 14 hours |
| COURSE_005 | Building AI Agents and Custom Joule Agents on SAP BTP | Advanced | 18 hours |

**Example record — COURSE_001**

```python
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
}
```

---

## 4. Required Structured Output

The assistant must return a Pydantic model, not a plain string.

### `RecommendationResponse`

| Field | Type | Description |
|---|---|---|
| `recommended_courses` | `List[str]` | Course IDs recommended for the learner, best first |
| `reason` | `str` | Concise explanation of why these courses fit the learner |
| `prerequisites` | `List[str]` | What the learner should have before starting |
| `learning_sequence` | `List[str]` | Ordered path of course IDs, first to last |
| `confidence` | `float` | 0.0 – 1.0, constrained with `ge=0.0, le=1.0` |

### `SourceMetadata` — provenance for one recommended course

| Field | Description |
|---|---|
| `course_id` | e.g. `COURSE_001` |
| `course_name` | Human-readable name |
| `experience_level` | Target experience level |
| `duration` | e.g. `"6 hours"` |
| `source` | Where the record came from, e.g. `courses.py::COURSE_001` |

### `FinalRecommendation` — extends `RecommendationResponse`

| Field | Description |
|---|---|
| `sources` | `List[SourceMetadata]` — one entry per recommended course |
| `total_learning_hours` | `int` — computed by the custom tool, **not** by the LLM |

---

## 5. Hands-on Tasks

### Task 1: Build the Course Documents

Convert each course dict into a LangChain `Document`. The page content should read as natural text so it embeds well; keep `course_id`, `course_name`, `experience_level`, and `duration` in metadata for source attribution.

### Task 2: Create Embeddings and the Vector Store

Use Gemini embeddings (`models/gemini-embedding-001`) and index the documents in a **FAISS** vector store.

### Task 3: Build the Retriever

Retrieve the top-k most semantically similar courses for a learner question. Verify that a question worded completely differently from the catalog text still retrieves the right course.

### Task 4: Write the RAG Prompt

The prompt must instruct Gemini to:

1. Answer **only** from the retrieved course records.
2. Never recommend a course that is not in the retrieved context.
3. Respect prerequisites — do not recommend an Advanced course to a complete beginner.
4. Return a learning sequence in a sensible order.
5. Give an honest confidence score.

### Task 5: Enforce Structured Output

Bind the `RecommendationResponse` schema to the model so the LLM output is **validated by Pydantic**. A response that does not conform must fail loudly rather than pass through as text.

### Task 6: Build a Custom Tool — `calculate_total_learning_hours`

```python
@tool
def calculate_total_learning_hours(course_ids: List[str]) -> int:
    """Sum the durations of the given courses."""
```

Parse the `"N hours"` duration strings and sum them. **Arithmetic must be done in Python, not by the LLM** — this is the point of the tool.

### Task 7: Add Conversation History

Implement a `ConversationHistory` class so follow-up questions keep context:

```
User: I am an ABAP developer new to AI. Where do I start?
Bot:  COURSE_001 …
User: And after that?
```

The second question must be understood as "what comes after COURSE_001".

### Task 8: Add Intent Routing

Not every message is a recommendation request. Build a `RouterDecision` Pydantic model:

| Field | Values | Meaning |
|---|---|---|
| `intent` | `recommend` / `general` | `recommend` = run the RAG pipeline; `general` = greetings, catalog browsing, questions about one course |
| `reply` | `str` | Filled **only** when intent is `general`; empty for `recommend` |

Greetings and small talk must not trigger a full retrieval + recommendation cycle.

### Task 9: Attach Source Metadata

For every recommended course ID, look up the catalog record and attach a `SourceMetadata` entry. Every recommendation must be traceable back to a specific course record.

### Task 10: Build the Streamlit Chat UI

Build a chat front end that displays the recommendation, the learning sequence, the confidence, the total learning hours, and the sources.

---

## 6. Test Questions

| Type | Question |
|---|---|
| **Beginner routing** | I am an SAP ABAP developer with no AI experience. Which course should I take first to learn SAP Business AI? |
| **Prerequisite awareness** | I want to build custom Joule agents. What do I need to learn first? |
| **Sequencing** | Give me a complete learning path from zero to building AI agents on SAP BTP. |
| **Tool usage** | How many total hours is the full learning path? |
| **Follow-up (history)** | *(after a recommendation)* And what comes after that? |
| **General intent** | Hi, what courses do you offer? |
| **Out of catalog** | Do you have a course on Kubernetes administration? |

The final question must **not** invent a course — the assistant should state that the catalog does not cover it.

---

## 7. Expected Output Structure

```json
{
  "recommended_courses": ["COURSE_001"],
  "reason": "As an SAP professional new to AI, start with the beginner course that introduces Generative AI, LLMs and SAP Business AI.",
  "prerequisites": ["Basic understanding of SAP applications"],
  "learning_sequence": ["COURSE_001", "COURSE_002", "COURSE_004"],
  "confidence": 0.92,
  "sources": [
    {
      "course_id": "COURSE_001",
      "course_name": "Introduction to Generative AI for SAP Professionals",
      "experience_level": "Beginner",
      "duration": "6 hours",
      "source": "courses.py::COURSE_001"
    }
  ],
  "total_learning_hours": 6
}
```

---

## 8. Evaluation Criteria

| Requirement | Done |
|---|---|
| Course catalog with all seven required fields | [ ] |
| Documents built with metadata preserved | [ ] |
| Gemini embeddings + FAISS vector store | [ ] |
| Semantic retrieval works on differently-worded questions | [ ] |
| Grounded prompt — no course invented outside the catalog | [ ] |
| Output validated as a Pydantic model | [ ] |
| Custom tool computes total learning hours in Python | [ ] |
| Conversation history supports follow-up questions | [ ] |
| Intent router separates `recommend` from `general` | [ ] |
| Source metadata attached to every recommendation | [ ] |
| Streamlit chat UI runs | [ ] |

## 9. Design Questions to Answer

1. Why is RAG a better fit than putting the whole catalog into the prompt?
2. Why is the total-hours calculation done by a tool instead of the LLM?
3. Why must `confidence` be constrained to 0.0–1.0 in the schema rather than trusted from the model?
4. What breaks if source metadata is dropped?
5. Why route `general` messages away from the RAG pipeline?
6. How would this design change if the catalog had 5,000 courses instead of 5?

## 10. Final Learning Outcome

After completing this exercise, the learner will be able to build a grounded RAG recommendation system, enforce validated structured output from an LLM, combine retrieval with a deterministic Python tool, maintain multi-turn conversation state, and expose the whole pipeline through a chat interface.
