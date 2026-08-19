# 📋 Viva Questions & Answers — Document Q&A RAG API

> **Project**: Documents Q&A API using RAG  
> **Tech Stack**: FastAPI · LangChain · Google Gemini · Pydantic · Uvicorn  
> **Scenario**: Accenture Hackathon — Agentic AI

---

## 🔹 Section 1 — Project Overview

### Q1. What is your project about? Give a brief overview.

**A:** Our project is a **Document Q&A API built with RAG (Retrieval-Augmented Generation)**. It lets users upload/ingest text documents, which get split into chunks and stored as embeddings. When a user asks a question, the system retrieves the most relevant chunks using cosine similarity and then uses Google Gemini LLM to generate a grounded answer — meaning the LLM only answers from the provided documents, not from its own training data.

---

### Q2. What problem does this project solve?

**A:** In large organisations like Accenture, employees often need quick answers from internal documents — HR policies, compliance docs, SOPs, etc. Manually searching through lengthy documents is time-consuming. Our API automates this by letting users simply **ask a question in natural language** and get an accurate, source-cited answer from ingested documents.

---

### Q3. What is the Hackathon scenario/theme you are working on?

**A:** The hackathon theme is **Agentic AI** — building AI systems that can autonomously perform tasks. Our project fits this by creating an **intelligent agent** that can autonomously ingest documents, understand their content via embeddings, retrieve relevant information, and generate grounded answers — all without human intervention in the pipeline.

---

## 🔹 Section 2 — Agentic AI Concepts

### Q4. What is Agentic AI?

**A:** Agentic AI refers to AI systems that can **act autonomously** to accomplish goals. Unlike traditional chatbots that just respond, agentic AI systems can:
- **Perceive** — take in information (our system ingests documents)
- **Reason** — understand context and relevance (embedding similarity search)
- **Act** — produce meaningful outputs (generate grounded answers)
- **Use tools** — interact with external systems (Google Gemini API, embedding models)

Our project demonstrates an agentic workflow where the AI agent autonomously retrieves context, reasons over it, and produces answers.

---

### Q5. How is your project an example of Agentic AI?

**A:** Our system is agentic because:
1. It **autonomously decides** which document chunks are relevant to a question (via cosine similarity ranking).
2. It **uses tools** — the embedding model and the LLM are tools the agent uses.
3. It **grounds its answers** — it doesn't hallucinate; it only uses extracted information and cites sources.
4. It follows a **structured workflow**: Ingest → Embed → Retrieve → Generate — without needing human guidance at each step.

---

### Q6. What is the difference between Agentic AI and a regular chatbot?

**A:**

| Aspect | Regular Chatbot | Agentic AI |
|--------|----------------|------------|
| Knowledge | Fixed training data only | Can dynamically ingest new data |
| Autonomy | Responds to prompts only | Can plan, retrieve, and act |
| Tools | No tool usage | Uses external tools (APIs, DBs, search) |
| Grounding | May hallucinate | Can be grounded to specific sources |
| Workflow | Single prompt → response | Multi-step pipeline |

---

## 🔹 Section 3 — RAG (Retrieval-Augmented Generation)

### Q7. What is RAG? Why did you use it?

**A:** **RAG = Retrieval-Augmented Generation**. It is a technique where instead of relying solely on the LLM's training data, we first **retrieve** relevant information from an external knowledge base, and then pass that as context to the LLM for **generation**.

**Why we used it:**
- **Reduces hallucination** — LLM only answers from provided documents.
- **Up-to-date knowledge** — We can ingest new documents anytime; no need to retrain the model.
- **Source citation** — We can tell the user exactly which document the answer came from.
- **Cost-effective** — Much cheaper than fine-tuning a model on custom data.

---

### Q8. Explain the RAG pipeline/workflow of your project.

**A:** Our RAG pipeline has two main phases:

**Phase 1 — Ingestion (`/ingest` endpoint):**
1. User sends documents (source name + text).
2. Text is split into smaller chunks using `RecursiveCharacterTextSplitter` (300 chars, 50 overlap).
3. Each chunk is converted into an embedding vector using Google's `gemini-embedding-001` model.
4. Chunks + embeddings are stored in an in-memory store (`chunks_store`).

**Phase 2 — Querying (`/ask` endpoint):**
1. User sends a question.
2. Question is embedded using the same embedding model.
3. Cosine similarity is computed between the question vector and all stored chunk vectors.
4. Top-K (3) most similar chunks are retrieved.
5. These chunks are formatted as numbered extracts and sent as context to Gemini LLM.
6. LLM generates a grounded answer using only the extracts and returns which extracts it used.
7. Source documents are mapped from used extracts and returned to the user.

---

### Q9. Why is RAG better than fine-tuning for this use case?

**A:**

| Aspect | RAG | Fine-Tuning |
|--------|-----|-------------|
| Cost | Low (just API calls) | High (GPU training) |
| Update data | Ingest new docs instantly | Retrain the model |
| Hallucination control | High (grounded to sources) | Medium |
| Source citation | Easy | Difficult |
| Setup complexity | Simple | Complex |

For a hackathon project dealing with frequently changing documents (HR policies etc.), RAG is the practical and scalable choice.

---

## 🔹 Section 4 — LangChain

### Q10. What is LangChain? Why did you use it?

**A:** **LangChain** is a Python framework for building applications powered by LLMs. It provides:
- **Standardized interfaces** for chat models, embeddings, and text splitters.
- **Model-agnostic wrappers** — easy to swap between OpenAI, Google Gemini, etc.
- **Built-in utilities** like text splitters, structured output parsing, prompt templates.

**Why we used it:**
- `ChatGoogleGenerativeAI` — gives us a clean interface to call Gemini for chat completions.
- `GoogleGenerativeAIEmbeddings` — simplifies embedding generation.
- `RecursiveCharacterTextSplitter` — handles intelligent text chunking.
- `.with_structured_output()` — lets us get responses as Pydantic models directly.

---

### Q11. What LangChain components are you using in the project?

**A:** We use three main LangChain components:

1. **`ChatGoogleGenerativeAI`** (from `langchain-google-genai`)
   - Wraps Google's Gemini chat model.
   - Used in the `/ask` endpoint to generate answers.
   - Called with `temperature=0` for deterministic, factual responses.

2. **`GoogleGenerativeAIEmbeddings`** (from `langchain-google-genai`)
   - Wraps Google's embedding model (`gemini-embedding-001`).
   - Used to embed both document chunks and user questions into vector space.

3. **`RecursiveCharacterTextSplitter`** (from `langchain-text-splitters`)
   - Splits large documents into smaller chunks (300 characters with 50-character overlap).
   - "Recursive" means it tries to split on natural boundaries (paragraphs → sentences → words) before falling back to character-level splitting.

---

### Q12. What is LangGraph? Did you use it? Why or why not?

**A:** **LangGraph** is a library (built on top of LangChain) for building **stateful, multi-step agent workflows** as graphs. It is useful when you need:
- Cyclic workflows (loops, retries)
- Multiple agents coordinating
- Complex decision trees with branching logic

**We did NOT use LangGraph** because our workflow is a **simple linear pipeline** (Ingest → Embed → Retrieve → Generate). There are no loops, no multi-agent coordination, and no conditional branching. Using LangGraph would be over-engineering for our use case. LangChain's core components were sufficient.

---

### Q13. What is the difference between LangChain and LangGraph?

**A:**

| Aspect | LangChain | LangGraph |
|--------|-----------|-----------|
| Purpose | Building LLM-powered apps | Building stateful agent workflows |
| Structure | Linear chains/pipelines | Graph-based (nodes + edges) |
| State management | Basic | Built-in state persistence |
| Best for | Simple RAG, chatbots, Q&A | Multi-agent systems, complex workflows |
| Complexity | Lower | Higher |

**Analogy**: LangChain is like a straight assembly line; LangGraph is like a flowchart with decision points and loops.

---

## 🔹 Section 5 — Technical Deep Dive

### Q14. What is an embedding? Why are embeddings important in your project?

**A:** An **embedding** is a numerical vector representation of text that captures its semantic meaning. Similar texts will have vectors that are close together in the vector space.

**Importance in our project:**
- We convert document chunks into embeddings to enable **semantic search**.
- When a user asks a question, we embed the question and find chunks whose embeddings are closest to it.
- This allows us to retrieve relevant information even if the exact words don't match (e.g., "leave policy" matches "annual leave: 18 days").

---

### Q15. What embedding model are you using and why?

**A:** We use **`gemini-embedding-001`** from Google. Reasons:
- It's from the same provider (Google) as our chat model, ensuring consistency.
- It produces high-quality embeddings optimized for semantic similarity.
- It's accessible via the same API key, simplifying configuration.
- It's cost-effective compared to alternatives.

---

### Q16. Explain cosine similarity. Why did you implement it manually?

**A:** **Cosine similarity** measures the cosine of the angle between two vectors. It ranges from -1 to 1:
- **1** → identical direction (very similar)
- **0** → perpendicular (unrelated)
- **-1** → opposite (very dissimilar)

**Formula:**
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**Why manually implemented:**
- We wanted to keep dependencies minimal — no need for NumPy or SciPy just for one function.
- It demonstrates understanding of the underlying math.
- Our implementation handles edge cases (zero-norm vectors return 0.0).

---

### Q17. What is `RecursiveCharacterTextSplitter`? Why this specific splitter?

**A:** It's a text splitter from LangChain that recursively splits text using a hierarchy of separators:
1. First tries to split on `\n\n` (paragraphs)
2. Then `\n` (lines)
3. Then ` ` (words)
4. Finally, individual characters

**Why this one:**
- It preserves semantic coherence — it tries to keep related text together.
- The `chunk_overlap=50` ensures context isn't lost at chunk boundaries.
- `chunk_size=300` keeps chunks small enough for precise retrieval but large enough to contain meaningful information.

---

### Q18. Why did you choose `chunk_size=300` and `chunk_overlap=50`?

**A:**
- **`chunk_size=300`**: Our documents (HR policies) are relatively short and structured. 300 characters is enough to capture a single policy point (e.g., annual leave rules) without mixing unrelated information.
- **`chunk_overlap=50`**: Overlap ensures that if a sentence is split across two chunks, both chunks contain enough context. 50 characters (~8-10 words) is sufficient overlap without causing excessive duplication.
- **`TOP_K=3`**: We retrieve 3 chunks because HR policies are concise — 3 relevant chunks usually cover the answer fully.

---

### Q19. Why are you using in-memory storage? What are its limitations?

**A:** 
**Why in-memory:**
- Simplicity — no database setup needed (ideal for a hackathon/prototype).
- Fast — no I/O latency for reads.
- Easy to understand and demo.

**Limitations:**
- **Data is lost on restart** — all ingested documents disappear when the server stops.
- **Not scalable** — for thousands of documents, cosine similarity over all chunks is O(n) per query.
- **No persistence** — no backup or recovery.

**Production alternative:** Use a vector database like **Pinecone, ChromaDB, Weaviate, or FAISS** for persistent, indexed, and scalable vector search.

---

### Q20. What is structured output? Why did you use `with_structured_output()`?

**A:** Structured output means getting the LLM to return data in a predefined schema instead of free-form text.

We use `llm.with_structured_output(GroundedAnswer)` which:
- Forces Gemini to return a response matching our `GroundedAnswer` Pydantic model.
- This gives us a clean `answer` string and a `used_extracts` list of integers.
- No need for manual parsing of LLM response — it's type-safe and reliable.

```python
class GroundedAnswer(BaseModel):
    answer: str
    used_extracts: list[int] = []
```

---

## 🔹 Section 6 — Framework & Architecture Choices

### Q21. Why FastAPI? Why not Flask or Django?

**A:**

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Speed | Async, very fast | Sync, moderate | Sync, moderate |
| Auto docs | Yes (Swagger UI at `/docs`) | No (needs extension) | No |
| Pydantic validation | Built-in | Manual | Forms-based |
| Type hints | First-class | Optional | Optional |
| Best for | APIs | Simple web apps | Full web apps |

FastAPI was ideal because:
- We're building a **pure API** (no frontend).
- Auto-generated Swagger docs make it easy to **demo and test**.
- Built-in Pydantic validation ensures **type-safe request/response**.
- Async support for handling concurrent requests.

---

### Q22. Why Google Gemini? Why not OpenAI GPT or other models?

**A:**
- **Free tier available** — important for a hackathon/student project.
- **High quality** — Gemini 3.5 Flash Lite is fast and capable for Q&A tasks.
- **Unified API** — same API key for both chat and embeddings.
- **LangChain integration** — `langchain-google-genai` provides ready-made wrappers.
- **Cost-effective** — significantly cheaper than GPT-4 for similar performance on this task.

---

### Q23. Explain the API endpoints of your project.

**A:** Our API has 4 endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root — redirects to docs |
| `/health` | GET | Health check — returns `{"status": "ok"}` |
| `/ingest` | POST | Accepts documents, chunks them, embeds them, stores them |
| `/ask` | POST | Accepts a question, retrieves relevant chunks, generates grounded answer |

**`/ingest` request:**
```json
{
  "documents": [
    {"source": "policy.txt", "text": "...document content..."}
  ]
}
```

**`/ask` request & response:**
```json
// Request
{"question": "How many annual leaves do I get?"}

// Response
{
  "answer": "You get 18 days of paid annual leave.",
  "source_used": ["hr_policy.txt"]
}
```

---

### Q24. What does the `@app.on_event("startup")` decorator do?

**A:** It registers a function that runs **once when the FastAPI server starts up**. In our case, it seeds the sample HR policy document into the chunks store so there's some data available for querying immediately — useful for demo purposes without needing to call `/ingest` first.

---

### Q25. Why Pydantic? What role does it play?

**A:** **Pydantic** is a data validation library. In our project:
- **Request validation** — `IngestRequest`, `AskRequest` models ensure incoming data has the correct structure.
- **Response serialization** — `IngestResponse`, `AskResponse` models define the exact shape of API responses.
- **Structured LLM output** — `GroundedAnswer` model is used with `with_structured_output()` to force the LLM to return typed data.
- **Auto-documentation** — FastAPI uses Pydantic models to generate Swagger/OpenAPI docs automatically.

---

## 🔹 Section 7 — Grounding & Hallucination

### Q26. What is grounding in LLMs? How does your project implement it?

**A:** **Grounding** means constraining the LLM to only use information from provided sources rather than its training data.

**Our implementation:**
1. The prompt explicitly instructs: *"Answer the question using only the extracts below."*
2. If the answer isn't in the extracts, the LLM must reply with the exact fallback message.
3. The LLM must list which extract numbers it used (`used_extracts`).
4. We map extract numbers back to source documents for citation.

This ensures **traceability** — every answer can be traced back to a specific document.

---

### Q27. What is hallucination in AI? How do you prevent it?

**A:** **Hallucination** is when an LLM generates information that sounds correct but is factually wrong or made up.

**Our prevention strategies:**
1. **RAG approach** — LLM only sees relevant document extracts, not open-ended questions.
2. **Explicit prompt instructions** — "Answer using ONLY the extracts."
3. **Fallback mechanism** — If info isn't in extracts, return a fixed fallback message instead of guessing.
4. **Temperature = 0** — Deterministic output, no creative/random responses.
5. **Source tracking** — `used_extracts` field verifies which sources were actually used.

---

## 🔹 Section 8 — Environment & Configuration

### Q28. What environment variables does your project use?

**A:**
- **`GOOGLE_API_KEY`** — API key for accessing Google Gemini services (chat + embeddings).
- **`GEMINI_CHAT_MODEL`** — Specifies which Gemini model to use for chat (e.g., `gemini-3.5-flash-lite`).
- **`GEMINI_EMBED_MODEL`** — Specifies the embedding model (defaults to `models/gemini-embedding-001`).

We use `python-dotenv` to load these from a `.env` file, keeping secrets out of source code.

---

### Q29. Why use `.env` files? What is `python-dotenv`?

**A:**
- **Security** — API keys should never be hardcoded in source code or committed to Git.
- **Flexibility** — Different environments (dev, staging, prod) can use different configs.
- **`python-dotenv`** reads key-value pairs from a `.env` file and loads them as environment variables.
- The `.env` file is listed in `.gitignore` so it's never pushed to the repository.
- `.env.example` provides a template showing required variables without exposing actual values.

---

## 🔹 Section 9 — Potential Follow-Up / Tricky Questions

### Q30. What would you change if this were a production system?

**A:**
1. **Vector database** — Replace in-memory store with ChromaDB/Pinecone/FAISS for persistence and scalable search.
2. **Authentication** — Add API key auth or OAuth to protect endpoints.
3. **File upload** — Accept PDF, DOCX files instead of raw text.
4. **Async processing** — Use background tasks for ingestion of large documents.
5. **Logging & monitoring** — Add structured logging, error tracking (Sentry), and metrics.
6. **Rate limiting** — Prevent API abuse.
7. **Caching** — Cache frequent queries to reduce LLM API costs.
8. **Testing** — Add unit tests, integration tests, and load tests.

---

### Q31. What is cosine similarity vs. Euclidean distance? Why cosine?

**A:**
- **Cosine similarity** — measures the **angle** between vectors (direction matters, not magnitude).
- **Euclidean distance** — measures the **straight-line distance** between vector endpoints.

**Why cosine:**
- Embeddings can have different magnitudes depending on text length.
- Cosine similarity is **magnitude-invariant** — it only cares about direction/meaning, not length.
- A short chunk about "leave policy" and a long chunk about "leave policy" will have similar cosine similarity to a question about leaves, even if their magnitudes differ.

---

### Q32. What is the `temperature` parameter? Why set it to 0?

**A:**
- **Temperature** controls the randomness of LLM output.
  - `0` → deterministic, always picks the most probable token.
  - `1` → more random/creative.
  - `>1` → very random.
- We set `temperature=0` because:
  - We want **factual, consistent answers** — same question should give same answer.
  - For a Q&A system, creativity is undesirable; accuracy is critical.

---

### Q33. What is TOP_K in your project? How does changing it affect results?

**A:** `TOP_K = 3` means we retrieve the **3 most similar chunks** to the user's question.

| TOP_K Value | Effect |
|-------------|--------|
| Too low (1) | May miss relevant context; incomplete answers |
| Optimal (3-5) | Good balance of relevance and context |
| Too high (10+) | Includes irrelevant chunks; confuses the LLM; higher cost |

For our HR policy documents which are short and focused, 3 chunks is optimal.

---

### Q34. What is `uvicorn`? Why use it?

**A:** **Uvicorn** is an ASGI (Asynchronous Server Gateway Interface) server for Python. It:
- Runs FastAPI applications.
- Supports async request handling.
- `reload=True` enables hot-reloading during development (server restarts on code changes).
- `host="127.0.0.1"` binds to localhost only (security — not exposed to network).
- `port=8000` is the standard development port.

---

### Q35. If a user asks a question NOT covered in the documents, what happens?

**A:**
1. The question still gets embedded and matched against chunks.
2. The top 3 chunks are still retrieved (even if similarity scores are low).
3. The prompt instructs the LLM: *"If the answer is not in the extracts, reply exactly: 'The information is not available in the provided documents'"*
4. The LLM returns the fallback message.
5. `used_extracts` will be empty `[]`.
6. `source_used` in the response will be an empty list `[]`.

---

### Q36. What are the limitations of your current approach?

**A:**
1. **In-memory storage** — data lost on restart.
2. **No file parsing** — only accepts plain text, not PDFs/DOCX.
3. **Linear search** — cosine similarity against all chunks is O(n); won't scale.
4. **Single model** — tied to Google Gemini; no model fallback.
5. **No conversation memory** — each question is independent; no follow-up context.
6. **No authentication** — anyone can access the API.
7. **No chunking strategies** — fixed character-based chunking; semantic chunking could be better.

---

### Q37. What is the role of `chunk_overlap` and why is it important?

**A:** Chunk overlap ensures that text near chunk boundaries isn't lost. Example:

Without overlap:
```
Chunk 1: "...leave must be submitted 5 days"
Chunk 2: "prior to taking leave in advance..."
```
→ The full instruction is split across two chunks; neither has the complete info.

With overlap (50 chars):
```
Chunk 1: "...leave must be submitted 5 days prior to taking"
Chunk 2: "submitted 5 days prior to taking leave in advance..."
```
→ Both chunks contain the critical phrase, improving retrieval accuracy.

---

### Q38. Explain the prompt engineering in your `/ask` endpoint.

**A:** Our prompt has four key parts:

1. **Role assignment**: `"You are an HR assistant"` — sets the persona and domain.
2. **Grounding instruction**: `"Answer using only the extracts below"` — prevents hallucination.
3. **Fallback instruction**: If answer isn't in extracts, use the exact fallback message — controls unknown-answer behavior.
4. **Source tracking**: `"List only the extract numbers you actually used"` — enables source citation.

The extracts are formatted as numbered blocks with source metadata:
```
[Extract 1 --source: hr_policy.txt]
<chunk text>
```

This structured format makes it easy for the LLM to reference specific extracts.

---

## 🔹 Section 10 — Quick Fire / Conceptual Questions

### Q39. What is an API? What is REST?

**A:** **API (Application Programming Interface)** is a set of rules that allows different software systems to communicate. **REST (Representational State Transfer)** is an architectural style where resources are accessed via standard HTTP methods (GET, POST, PUT, DELETE) at specific URLs (endpoints).

---

### Q40. What is ASGI vs WSGI?

**A:**
- **WSGI** (Web Server Gateway Interface) — synchronous, handles one request at a time per worker (Flask, Django).
- **ASGI** (Asynchronous Server Gateway Interface) — async, can handle multiple concurrent requests (FastAPI with Uvicorn).

FastAPI uses ASGI because it supports async operations, which is important when making API calls to Gemini (I/O-bound operations).

---

### Q41. What is a vector database? Name some examples.

**A:** A vector database is a specialized database designed to store, index, and search **vector embeddings** efficiently.

**Examples:**
- **ChromaDB** — open-source, easy to use, Python-native
- **Pinecone** — cloud-native, fully managed
- **FAISS** — Facebook's library for efficient similarity search
- **Weaviate** — open-source, supports hybrid search
- **Milvus** — open-source, built for scale

Our project uses a simple Python list as an in-memory vector store, which a vector DB would replace in production.

---

### Q42. What is semantic search? How is it different from keyword search?

**A:**
- **Keyword search** — matches exact words (e.g., searching "leave" only finds documents containing "leave").
- **Semantic search** — matches meaning (e.g., searching "vacation days" can find documents about "annual leave" because embeddings capture that these concepts are similar).

Our project uses semantic search via embeddings + cosine similarity.

---

### Q43. Can you explain the flow of data when a user asks a question?

**A:**
```
User Question ("How many leaves?")
       ↓
Embed question → vector [0.12, 0.85, ...]
       ↓
Compare with all stored chunk embeddings (cosine similarity)
       ↓
Rank chunks by similarity score
       ↓
Pick Top 3 chunks
       ↓
Format as numbered extracts with source info
       ↓
Build prompt: role + instructions + extracts + question
       ↓
Send to Gemini LLM (temperature=0)
       ↓
LLM returns GroundedAnswer (answer + used_extracts)
       ↓
Map extract numbers → source document names
       ↓
Return AskResponse (answer + source_used)
```

---

### Q44. What is `dict.fromkeys()` doing in your source mapping code?

**A:**
```python
sources = list(dict.fromkeys(
    top3[i-1][0]["source"] for i in result.used_extracts if 1 <= i <= len(top3)
))
```

This is a Python trick to **remove duplicates while preserving order**. If multiple extracts come from the same source document, we only list it once. `dict.fromkeys()` preserves insertion order (Python 3.7+) while eliminating duplicates — better than `set()` which doesn't guarantee order.

---

### Q45. What happens during the startup event in your app?

**A:** The `@app.on_event("startup")` function `seed_sample_docs()`:
1. Iterates over `SAMPLE_DOCUMENTS` (currently just `hr_policy.txt`).
2. Calls `ingest_document()` for each — splits text into chunks, embeds them, stores them.
3. Prints how many chunks were created.

This means the API has some data to query **immediately after startup**, even before any user calls `/ingest`. It's seeded with a sample HR policy for demo purposes.

---

> **💡 Tip for Viva**: Always relate your answers back to the project. Don't give generic textbook answers — show that you understand how each concept applies specifically to your Document Q&A system.

---

*Good luck with your viva! 🚀*
