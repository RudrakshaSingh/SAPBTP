# Problem Statement 16 — Multi-Document Q&A API with Source Filtering

| | |
|---|---|
| **Project Title** | Multi-Document Q&A API with Category-Based Source Filtering |
| **Domain** | Enterprise Knowledge Base (HR · IT · Finance) |
| **Topic** | RAG — chunk metadata, pre-retrieval filtering, source attribution |
| **Stack** | Python · FastAPI · Google Generative AI (embeddings + `gemini-2.5-flash`) |
| **Hands-on** | Hands-on 2 |
| **Builds on** | [Hands-on 1 — Document Q&A API using RAG](<15-document-qa-rag-fastapi(for HON).md>) |

---

## Goal

Extend your RAG API so it can hold documents from several different sources at once, remember which source each answer came from, and let the user restrict a question to just one source.

## 1. Business Scenario

A company now has three separate knowledge areas: **HR policies**, **IT support FAQs**, and **finance/reimbursement rules**. An employee asking about laptops should not get an answer pulled from the leave policy.

Example questions:

- "How do I reset my email password?" — *IT*
- "What is the travel reimbursement limit?" — *Finance*
- "How many casual leaves do I have?" — *HR*

## 2. What You Will Build

A FastAPI application that stores documents together with a category label, and lets the user optionally filter a question to a single category.

**Example input**

```json
{
  "question": "How do I reset my password?",
  "category": "IT"
}
```

**Example output**

```json
{
  "answer": "Go to the self-service portal and click Reset Password...",
  "category_searched": "IT",
  "sources_used": ["it_faq.txt"]
}
```

## 3. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/ingest` | Accepts document text plus a category label |
| `POST` | `/ask` | Accepts a question and an optional category filter |
| `GET` | `/sources` | Lists all categories and how many chunks each has |

## 4. Minimum Requirements

### A) Store documents with metadata

- Each chunk must remember its **category** (e.g., HR, IT, Finance) and **source name**.

### B) Filter before searching

- If the request includes a category, search **only** chunks in that category.
- If no category is given, search across **all** documents.

### C) Show where the answer came from

- The response must list the source(s) used to build the answer.

## 5. Constraints

- Still no external database — in-memory storage only.
- A wrong or unknown category should return a clear message, not crash.
- Output must always be valid JSON.

## 6. Evaluation Checklist (Your "Done" Criteria)

| Requirement | Done |
|---|---|
| Documents can be ingested under different categories | [ ] |
| A filtered question only uses chunks from that category | [ ] |
| An unfiltered question can pull from any category | [ ] |
| `/sources` correctly lists every category with a chunk count | [ ] |
| The answer always shows which source(s) it used | [ ] |

## 7. Sample Test Queries

| Category | Question |
|---|---|
| IT | "My VPN keeps disconnecting, what should I do?" |
| Finance | "What is the daily meal allowance on business trips?" |
| HR (no category filter) | "What are the working hours?" |
