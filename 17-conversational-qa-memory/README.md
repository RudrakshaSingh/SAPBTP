# Conversational Q&A API with Memory

A **FastAPI** HR chatbot that remembers the conversation. An employee can ask a follow-up like
_"And can I carry them over?"_ and still get a correct, grounded answer, because the API knows
_"them"_ means the annual leave from the question before. Every session has its own memory, and
two sessions never mix.

Hands-on 3, building on [16 — Multi-Document Q&A with Source Filtering](../16-multi-document-qa-source-filtering).
Still no vector database and no session database: chunks live in a Python list, conversations in
a dict.

Full brief: [problem statement 17](<../course-material/problem-statements/17-conversational-qa-memory(for HON).md>).

## The pipeline

```
POST /session/new   -> a fresh session_id, empty history

POST /chat          session_id + question
                    -> look up this session's history
                    -> rewrite the follow-up into a standalone question   <- the memory
                       "And can I carry them over?" -> "Can annual leave be carried over?"
                    -> cosine similarity against the HR chunks
                    -> top 3 extracts
                    -> Gemini, grounded prompt
                    -> save (question, answer) to the session
                    -> {"session_id": ..., "answer": ..., "sources_used": [...]}
```

The rewrite runs **before** retrieval. A search engine has no idea what _"them"_ is, so the
vague follow-up is turned into a self-contained question first, and only then searched. The
first message in a session has no history, so it is already standalone and skips the rewrite.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your key from https://aistudio.google.com/apikey

uvicorn app:app --reload      # http://127.0.0.1:8000/docs
```

Two HR documents (`hr_policy.txt`, `hr_parental_leave.txt`) load at startup, so `/chat` works
immediately.

## Endpoints

| Method | Path                     | Purpose                                                     |
| ------ | ------------------------ | ---------------------------------------------------------- |
| `GET`  | `/health`                | `{"status": "ok"}` plus how many documents and chunks load |
| `POST` | `/session/new`           | Starts a conversation and returns a unique `session_id`    |
| `POST` | `/chat`                  | Answers a question in a session, using its history         |
| `GET`  | `/session/{id}/history`  | Returns every message in that conversation                 |

```bash
# 1. start a conversation
curl -X POST http://127.0.0.1:8000/session/new
# -> {"session_id": "abc-123"}

# 2. first question (no history, asked as-is)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "question": "How many annual leave days do I get?"}'

# 3. follow-up -- "them" is resolved from the history
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "question": "And can I carry them over?"}'
```

```json
{
  "session_id": "abc-123",
  "answer": "Yes. A maximum of 10 unused annual leave days may be carried forward into the next calendar year, and they must be used before 31 March.",
  "sources_used": ["hr_policy.txt"]
}
```

## The memory, seen working

A three-turn conversation, each follow-up only making sense because of the turn before it:

```
Turn 1  "What is the maternity leave policy?"
        -> A female employee is entitled to 26 weeks of paid maternity leave for the first
           two children...                                    sources_used: ['hr_parental_leave.txt']

Turn 2  "How long is it?"                 (rewritten: "How long is maternity leave?")
        -> 26 weeks for the first two children, 12 weeks from the third onwards.

Turn 3  "Does it apply to adoption too?"  (rewritten: "Does maternity leave apply to adoption?")
        -> Yes. An employee who adopts a child below one year gets 26 weeks, on the same terms.
```

Ask _"How long is it?"_ with no history and retrieval has nothing to grab onto. With the
history, the follow-up becomes a real question first.

## Files

| File                             | Steps    | What it holds                                                    |
| -------------------------------- | -------- | ---------------------------------------------------------------- |
| [config.py](config.py)           | 1        | Model names, chunk size, top-k, the history window, `FALLBACK`   |
| [sample_data.py](sample_data.py) | 2        | Two HR documents, loaded at startup                              |
| [doc_qa.py](doc_qa.py)           | 3–4      | Chunking, embeddings, `DocumentStore`, search                    |
| [sessions.py](sessions.py)       | 5        | Per-session conversation history — Requirement A                 |
| [rag.py](rag.py)                 | 6–7      | Follow-up rewriting (B) and the grounded, cited answer (C)       |
| [models.py](models.py)           | 8        | Request and response schemas                                     |
| [app.py](app.py)                 | 9–11     | Startup, the four endpoints, and `python app.py`                 |

## Two decisions worth arguing with

| Decision                                          | Why                                                                                                                                                                                                                       |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rewrite the question, don't stuff the history into the answer prompt** | Retrieval is the part that needs the pronoun resolved. Fixing the question once, before the search, keeps the answer prompt small and the retrieval accurate — instead of hoping the model reads the whole transcript.   |
| **History stores the original question, not the rewrite**               | `/session/{id}/history` should read like the real chat the user had. The rewrite is an internal step; it never leaks into what the conversation looks like afterwards.                                                    |

## Evaluation criteria

| Requirement                                             | Where                                                            |
| ------------------------------------------------------- | --------------------------------------------------------------- |
| `/session/new` returns a unique `session_id`            | `SessionStore.new_session()` → `uuid4`                          |
| Follow-up questions answered using earlier context      | `rewrite_follow_up()` → `answer_question()`                     |
| History stored per session and can be retrieved         | `SessionStore.add_turn()` → `GET /session/{id}/history`         |
| Two different sessions stay completely separate          | `SessionStore._sessions` keyed by id; each owns its own list    |
| Answers remain grounded in the documents                | `RAG_PROMPT` + `FALLBACK` in [rag.py](rag.py)                   |
| The first question needs no rewriting                   | `rewrite_follow_up()` returns early when history is empty       |
| Every response is valid JSON                            | Pydantic response models on all four routes                    |
| No external database                                    | `DocumentStore.chunks` list + `SessionStore._sessions` dict    |

## Where to take it next

- **Persist sessions** — the dict dies with the process; move it to Redis or a table to survive
  a restart and to share across workers.
- **Expire old sessions** — nothing is ever evicted, so memory grows forever; a last-used
  timestamp and a sweep would cap it.
- **Feed history to the answer too** — for questions the rewrite can't fully capture, the answer
  prompt could see the last turn as well, at the cost of a bigger prompt.
- **Cite the rewrite** — return the standalone question in the response for debugging, so you can
  see exactly what was searched.

## Example — Seeing the memory work

Start the server and open **http://127.0.0.1:8000/docs**. That is Swagger UI: every endpoint
has a **Try it out** button, an editable request body and an **Execute** button, so the whole
walkthrough below is a handful of clicks and no curl.

**1. `GET /health`** — confirm what is loaded.

```json
{ "status": "ok", "documents": 2, "chunks": 6 }
```

**2. `POST /session/new`** — start a conversation. There is no body; just Execute.

```json
{ "session_id": "8f4c1e2a-..." }
```

Copy that `session_id` — every `/chat` call below uses it.

**3. `POST /chat`** — the first question. No history yet, so it is asked as-is.

```json
{ "session_id": "8f4c1e2a-...", "question": "How many annual leave days do I get?" }
```

```json
{
  "session_id": "8f4c1e2a-...",
  "answer": "Every confirmed full-time employee is entitled to 18 days of paid annual leave per calendar year. Leave accrues at 1.5 days per completed month of service.",
  "sources_used": ["hr_policy.txt"]
}
```

**4. `POST /chat` again — the follow-up.** Note that _"them"_ never names annual leave.

```json
{ "session_id": "8f4c1e2a-...", "question": "And can I carry them over?" }
```

```json
{
  "session_id": "8f4c1e2a-...",
  "answer": "Yes. A maximum of 10 unused annual leave days may be carried forward into the next calendar year, and they must be used before 31 March.",
  "sources_used": ["hr_policy.txt"]
}
```

This is the point of the exercise. Behind the scenes the API rewrote _"And can I carry them
over?"_ into _"Can annual leave be carried over?"_ using turn 3's history, **then** searched. Ask
the same follow-up in a brand-new session and it cannot — see step 6.

**5. `GET /session/{session_id}/history`** — paste the id into the path. This is the memory,
read back: the original questions the user typed, not the internal rewrites.

```json
{
  "session_id": "8f4c1e2a-...",
  "messages": [
    { "role": "user", "content": "How many annual leave days do I get?" },
    { "role": "assistant", "content": "Every confirmed full-time employee is entitled to 18 days..." },
    { "role": "user", "content": "And can I carry them over?" },
    { "role": "assistant", "content": "Yes. A maximum of 10 unused annual leave days..." }
  ]
}
```

**6. `POST /session/new`, then `POST /chat` — prove two sessions never mix.** Make a _second_
session and send it the follow-up with no lead-up:

```json
{ "session_id": "<the-new-id>", "question": "And can I carry them over?" }
```

```json
{
  "session_id": "<the-new-id>",
  "answer": "The information is not available in the provided documents.",
  "sources_used": []
}
```

Same words, different session, no history — so _"them"_ resolves to nothing and the search has
nothing to grab. The first session still answers it correctly. That difference **is** the
per-session memory.

Worth trying while you are in there:

- **The maternity thread** from the problem statement's sample test, in one session:
  _"What is the maternity leave policy?"_ → _"How long is it?"_ → _"Does it apply to adoption
  too?"_. Each follow-up is meaningless alone; each is answered correctly in context, all from
  `hr_parental_leave.txt`.
- **Ask _"How long is it?"_ as the very first message** of a fresh session. The fallback sentence
  comes back — there is nothing for _"it"_ to refer to yet.
- **Restart `uvicorn`** and reuse an old `session_id`. It is gone (404): sessions are a dict in
  memory and do not survive the process.
