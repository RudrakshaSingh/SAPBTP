# Problem Statement 15 — Document Q&A API using RAG

| | |
|---|---|
| **Project Title** | Document Q&A API using Retrieval-Augmented Generation |
| **Domain** | Human Resources / Internal Knowledge Base |
| **Topic** | RAG — chunking, embeddings, in-memory similarity search, grounded generation |
| **Stack** | Python · FastAPI · Google Generative AI (embeddings + `gemini-2.5-flash`) |
| **Hands-on** | Hands-on 1 |

---

## Goal

Build a FastAPI service that answers user questions using a set of documents you provide. Instead of the model making things up, it should retrieve the most relevant pieces of text and use them to write a grounded answer. This is the core idea of **Retrieval-Augmented Generation (RAG)**.

## 1. Business Scenario

A company keeps its HR policies in a few plain-text documents. Employees want to ask questions in natural language instead of scrolling through PDFs.

Example questions employees ask:

- "How many annual leave days do I get?"
- "What is the work-from-home policy?"
- "Can I carry forward unused leave?"

## 2. What You Will Build

A FastAPI application that lets a user (1) load documents into the system, and (2) ask a question and get an answer based only on those documents.

**Example input to the question endpoint**

```json
{
  "question": "How many annual leave days do I get?"
}
```

**Example output (structured)**

```json
{
  "answer": "Employees are entitled to 18 days of annual leave per year.",
  "sources_used": ["hr_policy.txt"]
}
```

## 3. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/ingest` | Accepts document text and stores it for searching |
| `POST` | `/ask` | Accepts a question and returns a grounded answer |

## 4. Minimum Requirements

### A) Ingest documents

- Accept one or more pieces of text through the `/ingest` endpoint.
- Split long text into smaller chunks so search works better.
- Create embeddings for each chunk using Google Generative AI and store them in memory.

### B) Retrieve relevant chunks

- Convert the user question into an embedding.
- Find the **top 3** most similar chunks using similarity search.

### C) Generate the answer

- Send the retrieved chunks plus the question to a Google Gemini model.
- Return an answer that uses **only** the retrieved text.
- If the answer is not in the documents, reply that the information is not available.

## 5. Constraints

- No external vector database — keep everything in memory (a Python list is fine).
- The output must always be valid JSON.
- The answer must be based on retrieved documents, not the model's own knowledge.

## 6. Evaluation Checklist (Your "Done" Criteria)

| Requirement | Done |
|---|---|
| `/health` returns a success response | [ ] |
| `/ingest` accepts text and confirms it was stored | [ ] |
| `/ask` returns a relevant, grounded answer for questions covered by the documents | [ ] |
| Out-of-scope questions get a clear "information not available" reply | [ ] |
| Every response is valid JSON | [ ] |

## 7. Sample Test Queries

| Question | Expected behaviour |
|---|---|
| "What is the notice period for resignation?" | Answered from the documents |
| "How many sick leaves are allowed per year?" | Answered from the documents |
| "Who is the current Prime Minister?" | Should say information not available |
