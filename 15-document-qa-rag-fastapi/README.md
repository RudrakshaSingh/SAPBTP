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

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | `{"status": "ok"}` plus how many documents and chunks are loaded |
| `POST` | `/ingest` | Chunks, embeds and stores one or more documents |
| `POST` | `/ask` | Answers a question from the stored documents |

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

| File | What it holds |
| --- | --- |
| [app.py](app.py) | The FastAPI app — request/response models and the three endpoints |
| [doc_qa.py](doc_qa.py) | Chunking, embeddings, `DocumentStore`, cosine search, grounded prompt |
| [sample_data.py](sample_data.py) | Three HR policy documents loaded at startup |
| [test_api.py](test_api.py) | Runs the sample queries in-process via `TestClient` |

## Three decisions worth arguing with

| Decision | Why |
| --- | --- |
| **Documents and questions are embedded differently** | The same sentence is stored as an *answer* but queried as a *question*. `doc_qa.py` keeps two embedders, `retrieval_document` and `retrieval_query`, and telling Gemini which role the text plays measurably sharpens retrieval. |
| **`sources_used` is what was *used*, not what was retrieved** | Retrieval always hands over three extracts, relevant or not. Returning all three sources would credit documents the answer never touched, so the model reports the extract numbers it drew on (`GroundedAnswer`, Pydantic structured output) and only those map to sources. Numbers outside the retrieved range are dropped rather than trusted. |
| **The fallback sentence cites nothing** | When the answer is not in the documents, `sources_used` comes back empty. Listing the three chunks that were retrieved anyway would imply the documents were consulted *and found to contain* an answer. |
| **`temperature=0`** | The answer should be a faithful reading of the retrieved text, not a fresh composition each time. |

Retrieval always returns the top 3 chunks — even for "Who is the current Prime Minister?"
Similarity search has no notion of "nothing matched", so the *prompt* is what refuses. That
guard rail is `FALLBACK` and rules 3–4 of `RAG_PROMPT` in [doc_qa.py](doc_qa.py).

## Evaluation criteria

| Requirement | Where |
| --- | --- |
| `/health` returns a success response | `health()` |
| `/ingest` accepts text and confirms it was stored | `ingest()` → `DocumentStore.add_document` |
| Long text is chunked | `chunk_text()` — `RecursiveCharacterTextSplitter` |
| Embeddings from Google Generative AI, stored in memory | `DocumentStore.__init__`, `self.chunks` |
| Top 3 chunks by similarity | `DocumentStore.search`, `TOP_K = 3` |
| Answer grounded in retrieved text only | `RAG_PROMPT`, `answer_question()` |
| Sources reported with the answer | `GroundedAnswer.used_extracts` → `Answer.sources_used` |
| Out-of-scope questions say so | `FALLBACK` |
| Every response is valid JSON | Pydantic response models on all three routes |
| No external vector database | `self.chunks: List[Chunk]` |

## Where to take it next

- **Persist the index** — the store dies with the process; pickle the vectors or move to
  FAISS once the corpus outgrows a list.
- **Cite the chunk, not just the file** — `Answer.chunks_used` already carries the extract
  and its score; surface them so an employee can check the exact clause.
- **Score threshold** — refuse before calling Gemini when the best similarity is below,
  say, 0.5, and save an LLM call on every out-of-scope question.
- **Upload real files** — accept PDF and DOCX via `UploadFile` and extract text with
  `pypdf` before chunking.
