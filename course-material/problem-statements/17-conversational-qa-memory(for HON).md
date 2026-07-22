# Problem Statement 17 — Conversational Q&A API with Memory

| | |
|---|---|
| **Project Title** | Conversational RAG Q&A API with Per-Session Memory |
| **Domain** | Human Resources / Internal Knowledge Base |
| **Topic** | Conversational RAG — session state, follow-up question rewriting, grounded answers |
| **Stack** | Python · FastAPI · Google Generative AI (embeddings + `gemini-2.5-flash`) |
| **Hands-on** | Hands-on 3 |
| **Builds on** | [Hands-on 2 — Multi-Document Q&A with Source Filtering](<16-multi-document-qa-source-filtering(for HON).md>) |

---

## Goal

Upgrade your RAG API into a chatbot that remembers the conversation. The user should be able to ask follow-up questions that depend on earlier ones, and still get correct, grounded answers.

## 1. Business Scenario

An employee is chatting with the HR assistant. A single answer often leads to a follow-up, and the follow-up only makes sense in the context of the previous questions.

Example conversation:

| Turn | User says | What they mean |
|---|---|---|
| 1 | "How many annual leave days do I get?" | — |
| 2 | "And can I carry them over?" | Carry over **annual leave** |
| 3 | "What about sick leave?" | How many **sick leave days** |

## 2. What You Will Build

A FastAPI application that keeps a separate conversation history for each user session and uses that history so follow-up questions are understood correctly.

**Example input**

```json
{
  "session_id": "abc-123",
  "question": "And can I carry them over?"
}
```

**Example output**

```json
{
  "session_id": "abc-123",
  "answer": "Yes, up to 10 unused annual leave days can be carried forward.",
  "sources_used": ["hr_policy.txt"]
}
```

## 3. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/session/new` | Creates a new conversation and returns a `session_id` |
| `POST` | `/chat` | Accepts a `session_id` and question, returns a grounded answer |
| `GET` | `/session/{id}/history` | Returns the messages in a conversation |

## 4. Minimum Requirements

### A) Manage sessions

- Each conversation has its own unique `session_id`.
- Store the question-and-answer history for each session in memory.

### B) Understand follow-up questions

- Before searching, use the previous messages to turn a vague follow-up into a clear, standalone question.
- Example: "And can I carry them over?" becomes "Can annual leave be carried over?"

### C) Answer using RAG

- Retrieve relevant chunks for the standalone question and generate a grounded answer.
- Add the new question and answer to the session history.

## 5. Constraints

- Different sessions must not mix their histories.
- The first question in a session has no history, so no rewriting is needed.
- Output must always be valid JSON.

## 6. Evaluation Checklist (Your "Done" Criteria)

| Requirement | Done |
|---|---|
| `/session/new` returns a unique `session_id` | [ ] |
| Follow-up questions are answered correctly using earlier context | [ ] |
| History is stored per session and can be retrieved | [ ] |
| Two different sessions stay completely separate | [ ] |
| Answers remain grounded in the documents | [ ] |

## 7. Sample Test Conversation

| Turn | Question |
|---|---|
| 1 | "What is the maternity leave policy?" |
| 2 | "How long is it?" |
| 3 | "Does it apply to adoption too?" |
