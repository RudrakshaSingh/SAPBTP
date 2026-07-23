# Multi-Document Q&A API with Source Filtering

A **FastAPI** service that holds several knowledge areas at once — **HR**, **IT**, **Finance** —
and lets a question be restricted to one of them. Every chunk remembers its category and its
file, so an employee asking IT about a password never gets an answer lifted from the leave
policy, and the reply always names the document it came from.

Hands-on 2, building on [15 — Document Q&A API using RAG](../15-document-qa-rag-fastapi).
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

| Method | Path       | Purpose                                                                      |
| ------ | ---------- | ---------------------------------------------------------------------------- |
| `GET`  | `/health`  | `{"status": "ok"}` plus how many categories, documents and chunks are loaded |
| `POST` | `/ingest`  | Chunks, embeds and stores one or more documents under a category             |
| `POST` | `/ask`     | Answers a question, optionally restricted to one category                    |
| `GET`  | `/sources` | Every category with its chunk count and the documents behind it              |

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

| File                             | Steps    | What it holds                                                    |
| -------------------------------- | -------- | ---------------------------------------------------------------- |
| [config.py](config.py)           | 1        | Model names, chunk size, top-k, the `FALLBACK` sentence          |
| [sample_data.py](sample_data.py) | 2        | Six documents across HR, IT and Finance, loaded at startup       |
| [doc_qa.py](doc_qa.py)           | 3–5      | Chunking, embeddings, `DocumentStore`, filtered search           |
| [rag.py](rag.py)                 | 6–7      | The grounded prompt and the cited answer                         |
| [models.py](models.py)           | 8        | Request and response schemas                                     |
| [app.py](app.py)                 | 9–11     | Startup, the four endpoints, and `python app.py`                 |

## Three decisions worth arguing with

| Decision                                                      | Why                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Categories are data, not an enum**                          | There is no hard-coded `HR / IT / Finance` list. A category exists because a document was ingested under it, so `/ingest` can open a whole new area at runtime — `test_api.py` adds `Legal` and immediately queries it. An enum would have needed a code change and a redeploy.                   |
| **Lookup is case-insensitive, display is not**                | `resolve_category` matches on a casefolded key but returns the spelling first used at ingest. Asking for `"legal"` searches `Legal` and the response says `Legal`, so `category_searched` never teaches the caller a spelling the store does not use.                                             |
| **An unknown category refuses, and says what exists**         | Falling back to searching everything would quietly ignore the filter the user asked for — worse than an error, because the answer looks right. `/ask` returns the normal JSON shape with the categories that do exist named in `answer` and `sources_used` empty. Same shape, HTTP 200, no crash. |

Retrieval always returns the top 3 chunks of the filtered set — even for "Who is the current
Prime Minister?", and even when the filter left nothing relevant behind. Similarity search has
no notion of "nothing matched", so the _prompt_ is what refuses. That guard rail is `FALLBACK`
and rules 3–4 of `RAG_PROMPT` in [rag.py](rag.py); rule 4 also stops the model from
answering an IT-scoped question out of its own knowledge just because it can guess that HR
would have known.

`sources_used` lists the documents the retrieved chunks came from, de-duplicated and kept in
rank order. It is what was _retrieved_, not what the model demonstrably leaned on, so an
answer drawn from one document may still cite a second that was retrieved alongside it.

## Evaluation criteria

| Requirement                                             | Where                                                             |
| ------------------------------------------------------- | ----------------------------------------------------------------- |
| Documents ingested under different categories           | `ingest()` → `DocumentStore.add_document(text, source, category)` |
| Each chunk remembers category and source                | `Chunk.category`, `Chunk.source`                                  |
| A filtered question only uses chunks from that category | `DocumentStore.search` — candidates filtered before scoring       |
| An unfiltered question can pull from any category       | `AskRequest.category = None` → `candidates = self.chunks`         |
| `/sources` lists every category with a chunk count      | `sources()` → `DocumentStore.chunk_counts()`                      |
| The answer always shows which source(s) it used         | `answer_question()` → `AskResponse.sources_used`                  |
| A wrong category returns a clear message, not a crash   | `resolve_category()` returning `None` → the message in `ask()`    |
| Out-of-scope questions say so                           | `FALLBACK`                                                        |
| Every response is valid JSON                            | Pydantic response models on all four routes                       |
| No external vector database                             | `self.chunks: List[Chunk]`                                        |

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

## Example Seeing it work — a new category, added at runtime

Start the server and open **http://127.0.0.1:8000/docs**. That is Swagger UI: every endpoint
has a **Try it out** button, an editable request body and an **Execute** button, so the whole
walkthrough below is five clicks and no curl.

**1. `GET /health`** — confirm what is loaded.

```json
{ "status": "ok", "categories": 3, "documents": 6, "chunks": 11 }
```

**2. `GET /sources`** — the same thing, broken down. This is the map of what `/ask` can reach,
and the list a caller reads before choosing a category.

```json
{
  "categories": [
    {
      "category": "HR",
      "chunks": 4,
      "sources": ["hr_leave_policy.txt", "hr_employment_terms.txt"]
    },
    {
      "category": "IT",
      "chunks": 4,
      "sources": ["it_faq.txt", "it_network_faq.txt"]
    },
    {
      "category": "Finance",
      "chunks": 3,
      "sources": [
        "finance_travel_policy.txt",
        "finance_reimbursement_rules.txt"
      ]
    }
  ],
  "total_documents": 6,
  "total_chunks": 11
}
```

**3. `POST /ask`** — ask about something none of the six documents covers, twice.

Unfiltered, the search runs and finds nothing usable:

```json
{ "question": "How do I replace a lost access card?" }
```

```json
{
  "answer": "The information is not available in the provided documents.",
  "category_searched": "all",
  "sources_used": []
}
```

Filtered to a category nobody has ingested, the search never runs at all:

```json
{ "question": "How do I replace a lost access card?", "category": "Facilities" }
```

```json
{
  "answer": "No documents are stored under category 'Facilities'. Available categories: HR, IT, Finance.",
  "category_searched": "Facilities",
  "sources_used": []
}
```

Two different refusals, and the difference matters. The first is the model saying _I looked and
it is not there_; the second is the API saying _there was nothing to look at_. Note that it does
not silently fall back to searching everything — that would answer a question the caller never
asked.

**4. `POST /ingest`** — open the category by ingesting into it. There is no enum to edit first.

```json
{
  "documents": [
    {
      "source": "office_facilities.txt",
      "category": "Facilities",
      "text": "Desk Booking\n\nEvery workstation in the office is booked through the facilities portal by 18:00 the previous day. Unclaimed desks are released 90 minutes after the start of the working day. Meeting rooms above 8 seats need the floor manager's approval.\n\nAccess Cards\n\nA lost access card is reported to reception the same day and replaced for 250 INR, deducted from the next payroll run. Temporary cards are issued for a maximum of 3 working days."
    }
  ]
}
```

```json
{
  "status": "stored",
  "ingested": [
    { "source": "office_facilities.txt", "category": "Facilities", "chunks": 1 }
  ],
  "total_chunks": 12
}
```

Paste the `text` as one line with `\n` escapes, as above — it is JSON, so a real line break
inside the string is a parse error. 445 characters is under the 800-character chunk size, so it
lands as a single chunk.

**5. `POST /ask` again — same question, and note the lower-case category.**

```json
{ "question": "How do I replace a lost access card?", "category": "facilities" }
```

```json
{
  "answer": "Report the lost access card to reception the same day. A replacement costs 250 INR, deducted from the next payroll run.",
  "category_searched": "Facilities",
  "sources_used": ["office_facilities.txt"]
}
```

Asked for `facilities`, searched `Facilities`, and said so — lookup is case-insensitive but the
response echoes the spelling the store actually uses. `GET /sources` now reports four categories
and 12 chunks. A knowledge area that did not exist two requests ago is queryable, with no code
change and no restart.

Worth trying while you are in there:

- **"How much allowance do I get?"** with `"category": "HR"` and then `"Finance"`. The corpus
  has a home-office allowance of 15,000 INR in HR and a meal allowance of 1,800 INR in Finance,
  and the question is too vague to separate them. The filter does it instead of the similarity
  score.
- **"How do I reset my password?"** with `"category": "HR"` — HR documents mention the HR portal
  repeatedly, so it retrieves confidently and still refuses, because none of what it retrieved
  says how to reset anything.
- **Drop the `category`** on any of these. `category_searched` comes back as `"all"` and the
  answer can come from anywhere.
- **Restart `uvicorn`** and repeat step 5 — back to the unknown-category refusal. The store is a
  list in memory, so ingested categories do not survive the process.
