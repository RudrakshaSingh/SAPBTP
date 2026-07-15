# Course Recommendation Assistant (RAG · LangChain · Gemini)

Final hands-on assignment: a Retrieval-Augmented Generation app that recommends
SAP + AI courses. Ask it a question in natural language and it returns a
**structured, source-attributed** recommendation.

> _I am an SAP ABAP developer with no AI experience. Which course should I take
> first to learn SAP Business AI?_

## What it does

- Indexes 5 sample courses (name, skills, level, duration, prerequisites) in a
  FAISS vector store using Gemini embeddings.
- Retrieves the most relevant courses for a question and asks Gemini to return
  structured output: `recommended_courses`, `reason`, `prerequisites`,
  `learning_sequence`, `confidence`.

### Bonus features (all implemented)

| # | Feature | Where |
|---|---------|-------|
| 1 | Custom tool for total learning hours | `calculate_total_learning_hours` in `rag_assistant.py` |
| 2 | Conversation history | `ConversationHistory` in `rag_assistant.py`, wired into the Streamlit chat |
| 3 | Result as a Pydantic model | `FinalRecommendation` in `models.py` |
| 4 | Source metadata per recommendation | `SourceMetadata` + `sources` field |
| 5 | Streamlit front end | `app.py` |

## Files

| File | Purpose |
|------|---------|
| `courses.py` | The 5 sample course documents |
| `models.py` | Pydantic models for structured output |
| `rag_assistant.py` | RAG pipeline, custom tool, conversation history, CLI demo |
| `app.py` | Streamlit chat UI |
| `requirements.txt` | Dependencies |
| `.env.example` | Copy to `.env` and add your API key |

## Setup

```bash
cd course-recommendation-assistant

# A virtual environment (.venv) is already included — just activate it.
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux (recreate if needed):
# python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt   # already installed if you use the bundled .venv

cp .env.example .env   # then edit .env and add your GOOGLE_API_KEY
```

Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Run

Command-line demo:

```bash
python rag_assistant.py
```

Streamlit web app:

```bash
streamlit run app.py
```

## Example output (structure)

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
