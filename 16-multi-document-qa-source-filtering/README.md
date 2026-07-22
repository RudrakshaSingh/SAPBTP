# Multi-Document Q&A API with Source Filtering

A **FastAPI** service that holds several knowledge areas at once — **HR**, **IT**, **Finance** —
and lets a question be restricted to one of them. Every chunk remembers its category and its
file, so an employee asking IT about a password never gets an answer lifted from the leave
policy, and the reply always names the document it came from.

Hands-on 2, building on [15 — Document Q&A API using RAG](<../15-document-qa-rag-fastapi>).
Still no vector database: chunks and embeddings live in a Python list.

Full brief: [problem statement 16](<../course-material/problem-statements/16-multi-document-qa-source-filtering(for HON).md>).

## The pipeline

```
POST /ingest    text + category -> chunk (800 chars, 120 overlap)
                                -> Gemini embeddings
                                -> list of Chunk(source, category, vector)

POST /ask       category?  -> keep only that category's chunks   <- the filter
                question   -> query embedding
                           -> cosine similarity against what survived the filter
                           -> top 3 extracts
                           -> Gemini, grounded prompt
                           -> {"answer": ..., "category_searched": ..., "sources_used": [...]}
```

The filter runs **before** the scoring, not after. A post-filter would let HR chunks fill the
top three and then hand back one IT chunk when three were asked for.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your key from https://aistudio.google.com/apikey

uvicorn app:app --reload      # http://127.0.0.1:8000/docs
python test_api.py            # the whole checklist in one go, no server needed
```

Six sample documents across HR, IT and Finance load at startup, so `/ask` works immediately.
Set `SEED_SAMPLE_DOCS=false` in `.env` to start empty and ingest your own.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | `{"status": "ok"}` plus how many categories, documents and chunks are loaded |
| `POST` | `/ingest` | Chunks, embeds and stores one or more documents under a category |
| `POST` | `/ask` | Answers a question, optionally restricted to one category |
| `GET` | `/sources` | Every category with its chunk count and the documents behind it |

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"source": "it_faq.txt", "category": "IT", "text": "Go to the self-service portal and click Reset Password."}]}'

curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?", "category": "IT"}'
```

```json
{
  "answer": "Go to the self-service portal at portal.company.local and click Reset Password. Enter your employee ID and the one-time code sent to your registered mobile number.",
  "category_searched": "IT",
  "sources_used": ["it_faq.txt"]
}
```

Omit `"category"` and the search spans everything; `category_searched` comes back as `"all"`.
`/ask` also accepts `"top_k"` (1–10, default 3) if you want to widen retrieval.

## The filter, seen working

Same question, two different scopes — from `python test_api.py`:

```
Q: How many casual leaves do I have?   (category: HR)
A: Employees receive 7 days of casual leave per calendar year...
   sources_used: ['hr_leave_policy.txt']

Q: How many casual leaves do I have?   (category: IT)
A: The information is not available in the provided documents.
   sources_used: []
```

The second one is the point of the exercise. The leave policy is by far the closest match in
the corpus, and the filter still wins.

## Files

| File | What it holds |
| --- | --- |
| [app.py](app.py) | The FastAPI app — request/response models and the four endpoints |
| [doc_qa.py](doc_qa.py) | Chunking, embeddings, `DocumentStore`, filtered search, grounded prompt |
| [sample_data.py](sample_data.py) | Six documents across HR, IT and Finance, loaded at startup |
| [test_api.py](test_api.py) | Runs the sample queries in-process via `TestClient` |

## Four decisions worth arguing with

| Decision | Why |
| --- | --- |
| **Categories are data, not an enum** | There is no hard-coded `HR / IT / Finance` list. A category exists because a document was ingested under it, so `/ingest` can open a whole new area at runtime — `test_api.py` adds `Legal` and immediately queries it. An enum would have needed a code change and a redeploy. |
| **Lookup is case-insensitive, display is not** | `resolve_category` matches on a casefolded key but returns the spelling first used at ingest. Asking for `"legal"` searches `Legal` and the response says `Legal`, so `category_searched` never teaches the caller a spelling the store does not use. |
| **An unknown category refuses, and says what exists** | Falling back to searching everything would quietly ignore the filter the user asked for — worse than an error, because the answer looks right. `/ask` returns the normal JSON shape with the categories that do exist named in `answer` and `sources_used` empty. Same shape, HTTP 200, no crash. |
| **`sources_used` is what was *used*, not what was retrieved** | Retrieval always hands over three extracts, relevant or not. The model reports the extract numbers it actually drew on (`GroundedAnswer`, Pydantic structured output) and only those map to sources. Numbers outside the retrieved range are dropped rather than trusted. |

Retrieval always returns the top 3 chunks of the filtered set — even for "Who is the current
Prime Minister?", and even when the filter left nothing relevant behind. Similarity search has
no notion of "nothing matched", so the *prompt* is what refuses. That guard rail is `FALLBACK`
and rules 3–4 of `RAG_PROMPT` in [doc_qa.py](doc_qa.py); rule 4 also stops the model from
answering an IT-scoped question out of its own knowledge just because it can guess that HR
would have known.

## Evaluation criteria

| Requirement | Where |
| --- | --- |
| Documents ingested under different categories | `ingest()` → `DocumentStore.add_document(text, source, category)` |
| Each chunk remembers category and source | `Chunk.category`, `Chunk.source` |
| A filtered question only uses chunks from that category | `DocumentStore.search` — candidates filtered before scoring |
| An unfiltered question can pull from any category | `AskRequest.category = None` → `candidates = self.chunks` |
| `/sources` lists every category with a chunk count | `sources()` → `DocumentStore.chunk_counts()` |
| The answer always shows which source(s) it used | `GroundedAnswer.used_extracts` → `Answer.sources_used` |
| A wrong category returns a clear message, not a crash | `resolve_category()` returning `None` → the message in `ask()` |
| Out-of-scope questions say so | `FALLBACK` |
| Every response is valid JSON | Pydantic response models on all four routes |
| No external vector database | `self.chunks: List[Chunk]` |

## Where to take it next

- **Filter on more than one axis** — `Chunk` could carry a date or an owning team just as
  cheaply; the search already takes a predicate in all but name.
- **Accept several categories** — `"category": ["IT", "Finance"]` for questions that
  legitimately straddle two areas, e.g. who pays for a lost laptop.
- **Route the category automatically** — one cheap classification call could pick the area when
  the caller does not, instead of always searching everything.
- **Score threshold** — refuse before calling Gemini when the best similarity is below, say,
  0.5, and save an LLM call on every out-of-scope question.
- **Persist the index** — the store dies with the process; pickle the vectors or move to FAISS
  once the corpus outgrows a list.
