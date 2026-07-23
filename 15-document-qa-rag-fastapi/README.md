# Document Q&A API using RAG

A **FastAPI** service that answers HR questions from your own documents. It retrieves the
most relevant passages first and asks **Google Gemini** to answer from those alone — so an
employee gets the policy that is written down, not the one the model imagines.

No vector database. Chunks and their embeddings live in a Python list, and retrieval is one
cosine similarity per chunk.

Full brief: [problem statement 15](<../course-material/problem-statements/15-document-qa-rag-fastapi(for HON).md>).

## The pipeline

```
POST /ingest    text -> chunk (800 chars, 120 overlap) -> Gemini embeddings -> list

POST /ask       question -> query embedding
                         -> cosine similarity against every chunk
                         -> top 3 extracts
                         -> Gemini, grounded prompt
                         -> {"answer": ..., "sources_used": [...]}
```

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your key from https://aistudio.google.com/apikey

uvicorn app:app --reload      # http://127.0.0.1:8000/docs
python test_api.py            # the whole checklist in one go, no server needed
```

The three sample HR documents load at startup, so `/ask` works immediately. Set
`SEED_SAMPLE_DOCS=false` in `.env` to start empty and ingest your own.

## Endpoints

| Method | Path      | Purpose                                                          |
| ------ | --------- | ---------------------------------------------------------------- |
| `GET`  | `/health` | `{"status": "ok"}` plus how many documents and chunks are loaded |
| `POST` | `/ingest` | Chunks, embeds and stores one or more documents                  |
| `POST` | `/ask`    | Answers a question from the stored documents                     |

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"source": "hr_policy.txt", "text": "Employees get 18 days of annual leave."}]}'

curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many annual leave days do I get?"}'
```

```json
{
  "answer": "Confirmed full-time employees are entitled to 18 days of paid annual leave per calendar year, accruing at 1.5 days per completed month of service.",
  "sources_used": ["hr_policy.txt"]
}
```

`/ask` also accepts `"top_k"` (1–10, default 3) if you want to widen retrieval.

## Files

| File                             | What it holds                                                         |
| -------------------------------- | --------------------------------------------------------------------- |
| [app.py](app.py)                 | The FastAPI app — request/response models and the three endpoints     |
| [doc_qa.py](doc_qa.py)           | Chunking, embeddings, `DocumentStore`, cosine search, grounded prompt |
| [sample_data.py](sample_data.py) | Three HR policy documents loaded at startup                           |
| [test_api.py](test_api.py)       | Runs the sample queries in-process via `TestClient`                   |

## Three decisions worth arguing with

| Decision                                                      | Why                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Documents and questions are embedded differently**          | The same sentence is stored as an _answer_ but queried as a _question_. `doc_qa.py` keeps two embedders, `retrieval_document` and `retrieval_query`, and telling Gemini which role the text plays measurably sharpens retrieval.                                                                                                                 |
| **`sources_used` is what was _used_, not what was retrieved** | Retrieval always hands over three extracts, relevant or not. Returning all three sources would credit documents the answer never touched, so the model reports the extract numbers it drew on (`GroundedAnswer`, Pydantic structured output) and only those map to sources. Numbers outside the retrieved range are dropped rather than trusted. |
| **The fallback sentence cites nothing**                       | When the answer is not in the documents, `sources_used` comes back empty. Listing the three chunks that were retrieved anyway would imply the documents were consulted _and found to contain_ an answer.                                                                                                                                         |
| **`temperature=0`**                                           | The answer should be a faithful reading of the retrieved text, not a fresh composition each time.                                                                                                                                                                                                                                                |

Retrieval always returns the top 3 chunks — even for "Who is the current Prime Minister?"
Similarity search has no notion of "nothing matched", so the _prompt_ is what refuses. That
guard rail is `FALLBACK` and rules 3–4 of `RAG_PROMPT` in [doc_qa.py](doc_qa.py).

## Evaluation criteria

| Requirement                                            | Where                                                  |
| ------------------------------------------------------ | ------------------------------------------------------ |
| `/health` returns a success response                   | `health()`                                             |
| `/ingest` accepts text and confirms it was stored      | `ingest()` → `DocumentStore.add_document`              |
| Long text is chunked                                   | `chunk_text()` — `RecursiveCharacterTextSplitter`      |
| Embeddings from Google Generative AI, stored in memory | `DocumentStore.__init__`, `self.chunks`                |
| Top 3 chunks by similarity                             | `DocumentStore.search`, `TOP_K = 3`                    |
| Answer grounded in retrieved text only                 | `RAG_PROMPT`, `answer_question()`                      |
| Sources reported with the answer                       | `GroundedAnswer.used_extracts` → `Answer.sources_used` |
| Out-of-scope questions say so                          | `FALLBACK`                                             |
| Every response is valid JSON                           | Pydantic response models on all three routes           |
| No external vector database                            | `self.chunks: List[Chunk]`                             |

## Where to take it next

- **Persist the index** — the store dies with the process; pickle the vectors or move to
  FAISS once the corpus outgrows a list.
- **Cite the chunk, not just the file** — `Answer.chunks_used` already carries the extract
  and its score; surface them so an employee can check the exact clause.
- **Score threshold** — refuse before calling Gemini when the best similarity is below,
  say, 0.5, and save an LLM call on every out-of-scope question.
- **Upload real files** — accept PDF and DOCX via `UploadFile` and extract text with
  `pypdf` before chunking.

## Example Seeing it work — the same question, before and after ingest

Start the server and open **http://127.0.0.1:8000/docs**. That is Swagger UI: every endpoint
has a **Try it out** button, an editable request body and an **Execute** button, so the whole
walkthrough below is four clicks and no curl.

**1. `GET /health`** — confirm what is loaded.

```json
{ "status": "ok", "documents": 3, "chunks": 6 }
```

The three seeded HR documents: leave, remote work, employment terms.

**2. `POST /ask`** — ask something they do not cover.

```json
{ "question": "How much per diem do I get for domestic travel?" }
```

```json
{
  "answer": "The information is not available in the provided documents.",
  "sources_used": []
}
```

Retrieval did not fail here — it returned its usual three chunks, whichever were nearest, and
`sources_used` is empty because none of them was used. The refusal came from the prompt.

**3. `POST /ingest`** — give it the missing document.

```json
{
  "documents": [
    {
      "source": "travel_policy.txt",
      "text": "Domestic Travel\n\nEmployees travelling within India receive a per diem of 2,000 INR per day for meals and incidentals. Hotel stays are capped at 4,500 INR per night in metro cities and 3,000 INR elsewhere. Airport transfers are reimbursed at actuals; personal expenses such as minibar and laundry are not.\n\nClaims\n\nExpense claims must be filed in the HR portal within 15 days of returning, with original receipts for anything above 500 INR. Claims filed after 30 days are not reimbursed."
    }
  ]
}
```

```json
{
  "status": "stored",
  "ingested": [{ "source": "travel_policy.txt", "chunks": 1 }],
  "total_chunks": 7
}
```

Paste the `text` as one line with `\n` escapes, as above — it is JSON, so a real line break
inside the string is a parse error. 486 characters is under the 800-character chunk size, so
it lands as a single chunk; a full policy of a few pages would come back as 8 or 10.

**4. `POST /ask` again — the exact same question.**

```json
{
  "answer": "Employees travelling within India receive a per diem of 2,000 INR per day for meals and incidentals.",
  "sources_used": ["travel_policy.txt"]
}
```

Nothing about the model changed between step 2 and step 4. No retraining, no restart, no prompt
edit — one more entry in a Python list, and the question is now answerable. That is the whole
argument for RAG, in two API calls.

Worth trying while you are in there:

- Ask **"How many days of annual leave do I get?"** — answered from `hr_policy.txt` from the
  first request, no ingest needed.
- Ask **"Who is the current Prime Minister?"** — the model knows, and refuses anyway. Out of
  scope is out of scope.
- Restart `uvicorn` and repeat step 4 — back to "not available". The store is a list in memory,
  so ingest does not survive the process.
