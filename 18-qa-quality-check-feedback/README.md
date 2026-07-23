# Q&A API with Answer Quality Check & Feedback

A **FastAPI** HR assistant with a quality layer. Every answer is checked against the documents
it was built from — is it actually **supported**, and how **confident** are we? — and employees
can thumbs-up / thumbs-down each answer so the team can see what is working.

Hands-on 4, building on [17 — Conversational Q&A API with Memory](../17-conversational-qa-memory).
Still no database: chunks live in a Python list and feedback in another.

Full brief: [problem statement 18](<../course-material/problem-statements/18-qa-quality-check-feedback(for HON).md>).

## The pipeline

```
POST /ingest    text -> chunk -> Gemini embeddings -> list of Chunk(source, vector)

POST /ask       question -> retrieve top 3 chunks (with similarity scores)
                         -> Gemini, grounded prompt            -> the answer
                         -> fact-checker sees ONLY those chunks -> supported?   <- the check
                         -> best similarity score               -> confidence
                         -> {"answer", "supported_by_documents", "confidence", "sources_used"}

POST /feedback           question + helpful(true/false)  -> stored in a list
GET  /feedback/summary                                   -> {total, helpful, not_helpful}
```

The check uses the **retrieved documents**, not the model's opinion of itself. `supported` comes
from a strict fact-checker that is shown only the retrieved extracts; `confidence` is the best
retrieval similarity score, a plain number. An answer we can't verify is not handed over — it is
replaced with the "not available" sentence.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your key from https://aistudio.google.com/apikey

uvicorn app:app --reload      # http://127.0.0.1:8000/docs
```

Two HR documents (`hr_policy.txt`, `hr_employment_terms.txt`) load at startup, so `/ask` works
immediately.

## Endpoints

| Method | Path                | Purpose                                                       |
| ------ | ------------------- | ------------------------------------------------------------ |
| `GET`  | `/health`           | `{"status": "ok"}` plus how many documents and chunks load   |
| `POST` | `/ingest`           | Chunks, embeds and stores one or more documents              |
| `POST` | `/ask`              | Answers a question **and** verifies the answer               |
| `POST` | `/feedback`         | Records whether an answer was helpful, returns updated totals |
| `GET`  | `/feedback/summary` | Totals: helpful vs not helpful                               |

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many annual leave days do I get?"}'
```

```json
{
  "answer": "Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per completed month of service.",
  "supported_by_documents": true,
  "confidence": "high",
  "sources_used": ["hr_policy.txt"]
}
```

```bash
curl -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"question": "How many annual leave days do I get?", "helpful": true}'
```

```json
{ "total": 1, "helpful": 1, "not_helpful": 0 }
```

## The quality check, seen working

Two questions, from the problem statement's sample test:

```
Q: What is the probation period?               (in the documents)
   answer:    New employees serve a probation period of 6 months...
   supported: true    confidence: medium

Q: What is the company's stock price today?    (nowhere in the documents)
   answer:    The information is not available in the provided documents.
   supported: false   confidence: low
```

The second one is the point. Nothing in the HR corpus is close to a stock price, so retrieval
scores low and the grounded prompt refuses — the API reports `supported: false` instead of
inventing a number.

## Files

| File                                     | Steps    | What it holds                                             |
| ---------------------------------------- | -------- | -------------------------------------------------------- |
| [config.py](config.py)                   | 1        | Model names, chunk size, top-k, confidence bands         |
| [sample_data.py](sample_data.py)         | 2        | Two HR documents, loaded at startup                      |
| [doc_qa.py](doc_qa.py)                   | 3–4      | Chunking, embeddings, `DocumentStore`, search            |
| [rag.py](rag.py)                         | 5        | The grounded answer                                      |
| [verify.py](verify.py)                   | 6        | The support check and confidence — Requirement A         |
| [feedback.py](feedback.py)               | 7        | Feedback storage and summary — Requirements B & C        |
| [models.py](models.py)                   | 8        | Request and response schemas                             |
| [app.py](app.py)                         | 9–11     | Startup, the five endpoints, and `python app.py`         |

## Two decisions worth arguing with

| Decision                                              | Why                                                                                                                                                                                                                                                       |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **The check is a fact-checker over the chunks, not the model rating itself** | Asking a model "are you sure?" just gets a confident guess. Instead the checker is shown **only** the retrieved extracts and asked whether every claim is backed by them — that is what "use the documents, not the model guessing" means.                |
| **An unsupported answer is withheld, not flagged and shown**                | If we can't verify it, showing it anyway invites someone to trust it. So `supported: false` comes back with the "not available" sentence and no sources — the honest outcome for a question the documents don't cover.                                    |

`confidence` is the best retrieval similarity score bucketed into **high / medium / low**
(thresholds in [config.py](config.py)). It measures how close the question sat to anything we
store — a document-based signal — so a question with no good match, like the stock price, lands
in `low`.

## Evaluation criteria

| Requirement                                                     | Where                                                    |
| --------------------------------------------------------------- | -------------------------------------------------------- |
| `/ask` returns an answer, a `supported` flag, and a confidence  | `ask()` → `AskResponse`                                  |
| The check uses the retrieved documents, not the model guessing  | `check_support()` — fact-checker over the extracts       |
| Unsupported answers are clearly flagged                         | `supported_by_documents=False` + the fallback sentence   |
| `/feedback` stores a helpful / not-helpful value                | `FeedbackStore.record()`                                 |
| `/feedback/summary` returns correct totals                      | `FeedbackStore.summary()`                                |
| Every response is valid JSON                                    | Pydantic response models on all five routes              |
| No external database                                            | `DocumentStore.chunks` list + `FeedbackStore._items` list |

## Where to take it next

- **Tie feedback to a specific answer** — store an answer id and let `/feedback` reference it,
  instead of matching on the question text.
- **Feed low-confidence questions back in** — a queue of questions that scored `low` is a
  ready-made list of gaps in the knowledge base.
- **Score threshold before the LLM** — if the best similarity is very low, refuse before calling
  Gemini at all and save the answer *and* the check calls.
- **Persist feedback** — the list dies with the process; a table would let the totals survive a
  restart and feed a real dashboard.

## Example — Seeing it work

Start the server and open **http://127.0.0.1:8000/docs**. That is Swagger UI: every endpoint
has a **Try it out** button, an editable request body and an **Execute** button, so the whole
walkthrough below is a handful of clicks and no curl.

**1. `GET /health`** — confirm what is loaded.

```json
{ "status": "ok", "documents": 2, "chunks": 6 }
```

**2. `POST /ask`** — a question the documents answer.

```json
{ "question": "What is the probation period?" }
```

```json
{
  "answer": "New employees serve a probation period of 6 months. Probation may be extended once, by up to 3 months.",
  "supported_by_documents": true,
  "confidence": "medium",
  "sources_used": ["hr_employment_terms.txt", "hr_policy.txt"]
}
```

Supported, so the answer is handed over with the documents behind it.

**3. `POST /ask` again** — a question the documents do **not** answer.

```json
{ "question": "What is the company's stock price today?" }
```

```json
{
  "answer": "The information is not available in the provided documents.",
  "supported_by_documents": false,
  "confidence": "low",
  "sources_used": []
}
```

The corpus has nothing close, so the check refuses rather than guessing a price. `supported` is
`false`, `confidence` is `low`, and no sources are cited — there was nothing to cite.

**4. `POST /feedback`** — the employee found the probation answer helpful.

```json
{ "question": "What is the probation period?", "helpful": true }
```

```json
{ "total": 1, "helpful": 1, "not_helpful": 0 }
```

Send a thumbs-down too, to see the totals move:

```json
{ "question": "What is the company's stock price today?", "helpful": false }
```

```json
{ "total": 2, "helpful": 1, "not_helpful": 1 }
```

**5. `GET /feedback/summary`** — the running tally, any time.

```json
{ "total": 2, "helpful": 1, "not_helpful": 1 }
```

Worth trying while you are in there:

- **"How many annual leave days do I get?"** — a direct hit, so `confidence` comes back `high`,
  higher than the probation question's `medium`. The band is the retrieval score: how close the
  question sat to stored text.
- **`POST /ingest`** a small document of your own, then ask about it — a brand-new fact becomes
  answerable and supported, with no restart.
- **Restart `uvicorn`** and call `/feedback/summary` — back to all zeros. Feedback is a list in
  memory and does not survive the process.
