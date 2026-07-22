# Problem Statement 18 — Q&A API with Answer Quality Check & Feedback

| | |
|---|---|
| **Project Title** | RAG Q&A API with Groundedness Verification and User Feedback |
| **Domain** | Human Resources / Internal Knowledge Base |
| **Topic** | RAG evaluation — groundedness check, confidence scoring, feedback capture |
| **Stack** | Python · FastAPI · Google Generative AI (embeddings + `gemini-2.5-flash`) |
| **Hands-on** | Hands-on 4 |
| **Builds on** | [Hands-on 3 — Conversational Q&A API with Memory](<17-conversational-qa-memory(for HON).md>) |

---

## Goal

Add a quality layer to your RAG API. Every answer should be checked to confirm it is actually supported by the retrieved documents (not made up), and users should be able to send feedback on whether an answer was helpful.

## 1. Business Scenario

The HR assistant is going live for real employees. Before trusting it, the team wants to know when an answer might be unreliable, and they want to collect feedback to improve it over time.

## 2. What You Will Build

A FastAPI application that returns an answer along with a confidence check, and that accepts thumbs-up / thumbs-down feedback which it stores and can summarize.

**Example output from the ask endpoint**

```json
{
  "answer": "Employees get 18 annual leave days per year.",
  "supported_by_documents": true,
  "confidence": "high",
  "sources_used": ["hr_policy.txt"]
}
```

**Example feedback input**

```json
{
  "question": "How many leave days do I get?",
  "helpful": true
}
```

## 3. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/ingest` | Stores document text for searching |
| `POST` | `/ask` | Returns an answer plus a quality check |
| `POST` | `/feedback` | Records whether an answer was helpful |
| `GET` | `/feedback/summary` | Returns totals: helpful vs not helpful |

## 4. Minimum Requirements

### A) Answer with a quality check

- After generating an answer, check whether it is actually supported by the retrieved chunks.
- Return a simple flag (`supported`: true/false) and a confidence level (**high** / **medium** / **low**).
- If the answer is not supported, tell the user the information may not be available.

### B) Collect feedback

- Accept a `helpful` (true/false) value from the user for an answer.
- Store all feedback in memory.

### C) Summarize feedback

- Return how many answers were marked helpful vs not helpful.

## 5. Constraints

- The quality check must use the retrieved documents, not the model guessing.
- Feedback storage can stay in memory (a list is fine).
- Output must always be valid JSON.

## 6. Evaluation Checklist (Your "Done" Criteria)

| Requirement | Done |
|---|---|
| `/ask` returns an answer, a `supported` flag, and a confidence level | [ ] |
| Unsupported answers are clearly flagged | [ ] |
| `/feedback` stores a helpful / not-helpful value | [ ] |
| `/feedback/summary` returns correct totals | [ ] |
| Every response is valid JSON | [ ] |

## 7. Sample Test Queries

| Question / Action | Expected behaviour |
|---|---|
| "What is the probation period?" | `supported = true` |
| "What is the company's stock price today?" | `supported = false` |
| Send feedback `helpful=false` | The summary totals update |
