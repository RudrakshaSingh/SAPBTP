# 🔍 Unit 9 — Retrieval Augmented Generation (RAG)

> **Module**: Module 4 — Generative AI  
> **Duration**: Day 16–17 (16 hours)  
> **Dates**: 20-Jul-2026, 21-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — RAG Fundamentals

### Q1. What is RAG (Retrieval-Augmented Generation)?

**A:** **RAG** is an architecture that enhances LLM responses by **retrieving relevant information from external knowledge sources** and injecting it into the prompt before generation.

```
Traditional LLM:  Question → LLM (uses only training data) → Answer
                   ⚠️ May hallucinate, knowledge is stale

RAG:  Question → Retrieve relevant docs → Inject as context → LLM → Grounded Answer
      ✅ Factual, up-to-date, source-cited
```

**Why RAG exists:**
- LLMs have a **knowledge cutoff** — they don't know about recent events.
- LLMs can **hallucinate** — generate plausible-sounding but false information.
- Organizations need answers from **their own private data** (HR policies, product docs).
- RAG provides **source attribution** — you can verify where the answer came from.

---

### Q2. What is the RAG pipeline? Explain each step.

**A:** RAG has two main phases: **Indexing** (offline) and **Querying** (online).

**Phase 1 — Indexing (Offline):**
```
Documents → Load → Split into chunks → Embed each chunk → Store in vector DB
```

| Step | What Happens | Tools |
|------|-------------|-------|
| **Load** | Read documents (PDF, TXT, HTML, CSV) | `SimpleDirectoryReader`, `PyPDF`, custom loaders |
| **Split/Chunk** | Break documents into smaller pieces | `RecursiveCharacterTextSplitter` |
| **Embed** | Convert chunks to vector representations | `GoogleGenerativeAIEmbeddings`, `text-embedding-ada-002` |
| **Store** | Save vectors in a searchable index | ChromaDB, Pinecone, FAISS, HANA Vector Engine |

**Phase 2 — Querying (Online):**
```
Question → Embed question → Find similar chunks → Build prompt → LLM → Answer
```

| Step | What Happens | Tools |
|------|-------------|-------|
| **Embed query** | Convert question to vector | `embed_query()` |
| **Retrieve** | Find top-K most similar chunks | Cosine similarity, vector DB search |
| **Augment** | Add retrieved chunks to LLM prompt | Prompt template with context |
| **Generate** | LLM produces grounded answer | Gemini, GPT-4, Claude |

---

### Q3. Why is RAG better than fine-tuning for knowledge retrieval?

**A:**

| Aspect | RAG | Fine-tuning |
|--------|-----|-------------|
| **Data freshness** | Real-time (add/remove docs anytime) | Stale until retrained |
| **Cost** | Low (just API calls + vector DB) | High (GPU training) |
| **Setup time** | Hours | Days to weeks |
| **Source citation** | ✅ Yes (can cite exact documents) | ❌ No (knowledge baked into weights) |
| **Hallucination** | Lower (grounded in retrieved context) | Can still hallucinate |
| **Data privacy** | Data stays in your vector DB | Data used in training (may leak) |
| **Scalability** | Add new docs without retraining | Must retrain for new data |
| **Best for** | Document Q&A, knowledge bases | Style, format, domain language |

**Rule of thumb:**
- **RAG** when the answer is IN the documents.
- **Fine-tuning** when you need to change HOW the model responds.

---

## 🔹 Section 2 — Document Processing & Chunking

### Q4. What is document loading? What types of documents can be loaded?

**A:** Document loading converts various file formats into text that can be processed by the RAG pipeline.

| Format | Loader | Challenge |
|--------|--------|-----------|
| **Plain text (.txt)** | Direct read | Simplest |
| **PDF** | PyPDF, PDFPlumber, Unstructured | Tables, images, multi-column layouts |
| **Word (.docx)** | python-docx | Formatting, headers/footers |
| **HTML** | BeautifulSoup, Unstructured | Remove tags, extract content |
| **CSV/Excel** | Pandas, CSVLoader | Structured → text conversion |
| **Markdown** | Direct read | Simple |
| **PowerPoint** | python-pptx | Slide-by-slide extraction |
| **Images** | OCR (Tesseract), Vision models | Accuracy depends on image quality |

```python
# LangChain document loaders
from langchain_community.document_loaders import TextLoader, PyPDFLoader

loader = PyPDFLoader("policy.pdf")
documents = loader.load()  # Returns list of Document objects
# Each Document has: page_content (text) + metadata (source, page, etc.)
```

---

### Q5. What is text chunking? Why do we need it?

**A:** **Chunking** = splitting documents into smaller, manageable pieces. It's necessary because:

1. **Context window limits** — LLMs can only process limited tokens.
2. **Relevance** — Smaller chunks are more likely to be fully relevant to a query.
3. **Embedding quality** — Embedding models work best on focused text, not entire documents.
4. **Precision** — Retrieving a small, targeted chunk is better than retrieving an entire 50-page document.

---

### Q6. What are the different chunking strategies?

**A:**

| Strategy | How It Works | Pros | Cons |
|----------|-------------|------|------|
| **Fixed-size** | Split every N characters/tokens | Simple, predictable | May split mid-sentence |
| **Recursive** | Split by separators (paragraphs → sentences → words) | Respects structure | Slightly complex |
| **Sentence-based** | Split on sentence boundaries | Natural boundaries | Varying chunk sizes |
| **Semantic** | Split based on topic/meaning changes | Best relevance | Slowest, needs model |
| **Document-structure** | Split by headings, sections, pages | Preserves document structure | Format-dependent |

**RecursiveCharacterTextSplitter (most common):**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,         # Max characters per chunk
    chunk_overlap=50,       # Characters shared between adjacent chunks
    separators=["\n\n", "\n", ". ", " ", ""]  # Try splitting by these, in order
)

chunks = splitter.split_text(document_text)
```

**How it works:**
1. Try to split by `\n\n` (paragraphs) first.
2. If chunks are still too large, split by `\n` (lines).
3. If still too large, split by `. ` (sentences).
4. Last resort: split by spaces or individual characters.

---

### Q7. How do you choose chunk size and overlap?

**A:**

| Parameter | Small Value | Large Value |
|-----------|-------------|-------------|
| **chunk_size** | More precise retrieval; may lose context | More context; may include irrelevant text |
| **chunk_overlap** | Potential information loss at boundaries | Redundancy; captures boundary context |

**Guidelines:**

| chunk_size | chunk_overlap | Use Case |
|-----------|---------------|----------|
| 200-300 | 20-50 | Short, factual documents (FAQ, policies) |
| 500-1000 | 50-100 | General documents (articles, reports) |
| 1000-2000 | 100-200 | Technical documents with complex context |

**Our hackathon project:** `chunk_size=300, chunk_overlap=50` — optimized for short HR policy documents.

**Trade-offs:**
- Too small → Loses context; "18 days annual leave" might be in one chunk without explaining eligibility.
- Too large → Too much irrelevant information; cosine similarity becomes noisy.
- Overlap → Ensures information at chunk boundaries isn't lost. If a sentence spans two chunks, overlap captures it in both.

---

## 🔹 Section 3 — Embeddings & Vector Search

### Q8. How do embeddings work in RAG?

**A:** Embeddings convert text into dense numerical vectors that capture semantic meaning.

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Embed a document chunk
doc_vector = embeddings_model.embed_documents(["Annual leave is 18 days"])
# Returns: [[0.023, -0.041, 0.089, ...]]  (768 dimensions)

# Embed a query
query_vector = embeddings_model.embed_query("How many leaves do I get?")
# Returns: [0.025, -0.038, 0.091, ...]    (768 dimensions)

# These vectors are CLOSE in vector space because they're semantically similar
```

**Key properties:**
- Semantically similar texts → similar vectors → high cosine similarity.
- The embedding captures **meaning**, not just keywords.
- "vacation days", "annual leave", "PTO" → all have similar embeddings.

---

### Q9. What is cosine similarity? Why is it used for RAG retrieval?

**A:** **Cosine similarity** measures the angle between two vectors. Value ranges from -1 (opposite) to 1 (identical).

```
cos(θ) = (A · B) / (||A|| × ||B||)

A · B     = Σ(aᵢ × bᵢ)     → dot product
||A||     = √(Σ aᵢ²)        → magnitude
```

**Why cosine over Euclidean distance:**
- **Magnitude-invariant** — A short chunk and a long chunk about the same topic still match well.
- **Works well in high dimensions** — Euclidean distance becomes less meaningful in 768+ dimensions.
- **Normalized** — Output is always between -1 and 1 (easy to compare and threshold).

**Our implementation:**
```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
```

---

### Q10. What is Top-K retrieval? How do you choose K?

**A:** **Top-K** means retrieving the K most similar chunks for a given query.

| K Value | Effect |
|---------|--------|
| K=1 | Only the single best match; may miss relevant info |
| K=3 (our choice) | Good balance of relevance and coverage |
| K=5-10 | More comprehensive; risk of including irrelevant chunks |
| K=20+ | Likely includes noise; may confuse the LLM |

**Choosing K depends on:**
- **Context window** — More chunks = more tokens. Don't exceed the model's limit.
- **Chunk size** — Larger chunks → lower K. Smaller chunks → higher K.
- **Task** — Factual Q&A → lower K. Research/summary → higher K.
- **Document diversity** — If answer might span multiple documents → higher K.

**Alternative: Similarity threshold** — Instead of top-K, retrieve all chunks with similarity > threshold (e.g., 0.7).

---

### Q11. What are the different retrieval strategies beyond basic vector search?

**A:**

| Strategy | How It Works | When to Use |
|----------|-------------|-------------|
| **Dense retrieval** | Embedding-based cosine similarity | Default RAG approach |
| **Sparse retrieval** | Keyword-based (BM25, TF-IDF) | When exact terms matter (legal, medical) |
| **Hybrid retrieval** | Combine dense + sparse scores | Best of both worlds |
| **Re-ranking** | Use a cross-encoder to re-score top candidates | Improve precision after initial retrieval |
| **Multi-query** | Generate multiple query variants, retrieve for each | Handle ambiguous queries |
| **HyDE** | Generate a hypothetical answer, embed THAT for retrieval | Improve retrieval when query is vague |
| **Parent-child** | Store small chunks for retrieval, return larger parent chunk | Get precise match + full context |

**Hybrid retrieval example:**
```python
# Score = α × vector_score + (1-α) × keyword_score
# α = 0.7 → 70% semantic, 30% keyword
```

---

## 🔹 Section 4 — RAG Prompt Design

### Q12. How do you design the RAG prompt?

**A:** The RAG prompt must instruct the LLM to use ONLY the retrieved context.

```python
prompt = """You are an HR assistant.
Answer the question using ONLY the extracts below.
If the answer is not in the extracts, reply exactly:
'Sorry, I could not find information related to your query in the available documents.'

In used_extracts, list only the extract numbers you actually used.
If answered with the fallback message, leave used_extracts empty.

Extracts:
{context}

Question: {question}"""
```

**Critical elements:**
1. **Role** — "You are an HR assistant" → domain-appropriate responses.
2. **Grounding instruction** — "ONLY the extracts below" → prevents hallucination.
3. **Fallback behavior** — Explicit message for unanswerable questions.
4. **Source tracking** — "list extract numbers you used" → enables citation.
5. **Context** — The retrieved chunks with source metadata.
6. **Question** — The user's query.

---

### Q13. What is context window management in RAG?

**A:** You must fit retrieved chunks + system prompt + question + expected answer all within the model's context window.

```
Context Budget:
  Model context window:       128,000 tokens
  System prompt:               -200 tokens
  Question:                     -50 tokens
  Expected answer:             -500 tokens
  Safety margin:               -250 tokens
  ─────────────────────────────────────────
  Available for context:      127,000 tokens

  Each chunk ≈ 100 tokens (chunk_size=300 chars)
  Max chunks retrievable:     ~1,270
```

**Strategies when context is limited:**
- **Reduce chunk size** — Smaller chunks = more can fit.
- **Reduce K** — Fewer chunks per query.
- **Summarize chunks** — Compress retrieved text before injection.
- **Map-reduce** — Process chunks in batches, combine summaries.
- **Use models with larger context windows** (Gemini 1M tokens).

---

### Q14. What is the "Lost in the Middle" problem?

**A:** LLMs tend to pay more attention to information at the **beginning and end** of the context window, and less to information in the **middle**.

```
Chunk 1 (beginning): High attention ✅
Chunk 2: Moderate
Chunk 3: Moderate
Chunk 4 (middle): LOW attention ⚠️
Chunk 5: Moderate
Chunk 6: Moderate
Chunk 7 (end): High attention ✅
```

**Mitigations:**
- **Reorder chunks** — Put the most relevant chunks at the beginning and end.
- **Reduce context** — Fewer chunks = less "middle."
- **Use smaller models less** — Larger models handle this better.
- **Map-reduce approach** — Process each chunk separately, then combine.

---

## 🔹 Section 5 — Advanced RAG Patterns

### Q15. What is Naive RAG vs. Advanced RAG?

**A:**

| Aspect | Naive RAG | Advanced RAG |
|--------|----------|-------------|
| **Retrieval** | Simple top-K vector search | Hybrid search, re-ranking, multi-query |
| **Chunking** | Fixed-size | Semantic, hierarchical |
| **Query** | Direct user question | Query rewriting, expansion |
| **Context** | Raw chunks in prompt | Compressed, summarized, reordered |
| **Evaluation** | Manual inspection | Automated metrics (RAGAS) |
| **Our project** | ✅ Naive RAG | Future improvement |

---

### Q16. What is query rewriting / query expansion?

**A:** **Query rewriting** transforms the user's question into a better query for retrieval.

```
Original query: "leaves"
→ Too vague for retrieval

Rewritten query: "annual leave policy days off vacation entitlement"
→ Multiple terms improve recall

# Using an LLM to rewrite:
prompt = "Rewrite this user question as a search query for an HR policy database.
          Add related terms and synonyms.
          Question: {user_question}"
```

**Multi-query approach:**
```
Original: "How many leaves do I get?"
→ Query 1: "annual leave entitlement days"
→ Query 2: "paid time off policy"
→ Query 3: "vacation days allowed per year"
# Retrieve for all three, merge and deduplicate results
```

---

### Q17. What is a re-ranker?

**A:** A **re-ranker** is a more accurate (but slower) model that re-scores the initial retrieval results to improve ranking.

```
Step 1: Vector search → Top 20 chunks (fast, approximate)
Step 2: Re-ranker → Re-score these 20 → Top 5 (slow, accurate)
Step 3: Use Top 5 in RAG prompt
```

**Why re-ranking works better:**
- **Vector search (bi-encoder):** Embeds query and documents independently → fast but approximate.
- **Re-ranker (cross-encoder):** Processes query AND document TOGETHER → more accurate but slower.

**Tools:** Cohere Rerank, `ms-marco-MiniLM-L-6-v2`, `BGE-reranker`.

---

### Q18. What is Corrective RAG (CRAG)?

**A:** **CRAG** adds a **self-correction step** after retrieval to evaluate whether retrieved documents are actually relevant.

```
1. Retrieve documents
2. Grade each document: "Is this relevant to the question?"
3. If relevant → use in prompt
4. If not relevant → try alternative retrieval (web search, different query)
5. If no relevant docs found → tell user "I don't have this information"
```

This prevents the LLM from trying to answer from irrelevant context.

---

### Q19. What is Self-RAG?

**A:** **Self-RAG** adds **reflection and critique** steps where the model evaluates its own retrieval and generation quality.

```
1. Decide: "Do I need to retrieve?" (some questions don't need docs)
2. Retrieve if needed
3. Grade: "Are these docs relevant?"
4. Generate answer
5. Critique: "Is my answer supported by the docs?"
6. Critique: "Is my answer useful?"
7. If not → regenerate with different approach
```

---

### Q20. What is Graph RAG?

**A:** **Graph RAG** combines traditional RAG with **knowledge graphs** — structured representations of entities and their relationships.

```
Traditional RAG: "Who is the CEO of Apple?"
→ Searches document chunks containing "CEO" and "Apple"

Graph RAG: "Who is the CEO of Apple?"
→ Looks up: Apple → (CEO_OF) → Tim Cook
→ Also finds: Tim Cook → (REPORTS_TO) → Board of Directors
→ More structured, relationship-aware retrieval
```

**Use cases:** Complex queries involving relationships, multi-hop reasoning, structured enterprise data.

---

## 🔹 Section 6 — RAG Evaluation

### Q21. How do you evaluate a RAG system?

**A:** RAG evaluation has two parts: **retrieval quality** and **generation quality**.

**Retrieval Metrics:**

| Metric | What It Measures |
|--------|------------------|
| **Context Precision** | Are the retrieved docs relevant? |
| **Context Recall** | Did we retrieve ALL relevant docs? |
| **Hit Rate** | Was the answer in at least one retrieved doc? |
| **MRR (Mean Reciprocal Rank)** | How high is the relevant doc ranked? |

**Generation Metrics:**

| Metric | What It Measures |
|--------|------------------|
| **Faithfulness** | Is the answer supported by retrieved context? (No hallucination) |
| **Answer Relevancy** | Does the answer address the question? |
| **Answer Correctness** | Is the answer factually correct? |

**RAGAS framework:**
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

result = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, answer_relevancy, context_precision]
)
print(result)
```

---

### Q22. What are common failure modes in RAG?

**A:**

| Failure Mode | Cause | Fix |
|-------------|-------|-----|
| **Wrong chunks retrieved** | Poor embedding, bad chunk boundaries | Better chunking, hybrid search |
| **Answer not in chunks** | Relevant chunk not retrieved; K too low | Increase K, use multi-query |
| **Hallucination** | LLM adds info not in context | Stronger grounding prompt, temp=0 |
| **Irrelevant answer** | Question misunderstood | Query rewriting, better prompt |
| **Too much context** | Too many chunks confuse LLM | Lower K, re-ranking |
| **Outdated info** | Stale documents in vector store | Regular re-ingestion pipeline |
| **Chunk boundary split** | Important info split across chunks | Increase chunk_overlap |

---

## 🔹 Section 7 — RAG in Production

### Q23. How do you deploy a RAG system in production?

**A:**

| Component | Development | Production |
|-----------|-------------|------------|
| **Vector store** | In-memory (list) / ChromaDB local | Pinecone, Weaviate, HANA Vector Engine |
| **Embedding** | API calls | Cached embeddings, batch processing |
| **LLM** | Direct API | Load balancer, retries, fallback models |
| **Documents** | Manual upload | Automated ingestion pipeline |
| **Monitoring** | Print statements | LangSmith, logging, alerting |
| **Caching** | None | Cache frequent queries + responses |
| **Auth** | None | API keys, JWT, OAuth |
| **Scaling** | Single process | Kubernetes, auto-scaling |

---

### Q24. How do you handle document updates in a RAG system?

**A:**

| Strategy | How It Works | Trade-off |
|----------|-------------|-----------|
| **Full re-index** | Delete all, re-embed everything | Simple but slow; expensive for large corpora |
| **Incremental update** | Track changes, only embed new/modified docs | Complex but efficient |
| **Versioned index** | Create new index version, swap atomically | No downtime, rollback support |
| **TTL (Time-to-Live)** | Auto-expire old embeddings | Works for time-sensitive data |

```python
# Incremental update pattern:
def update_documents(new_docs, modified_docs, deleted_doc_ids):
    # 1. Remove deleted documents
    vector_store.delete(filter={"doc_id": {"$in": deleted_doc_ids}})

    # 2. Remove old versions of modified docs
    vector_store.delete(filter={"doc_id": {"$in": [d.id for d in modified_docs]}})

    # 3. Add new and modified documents
    all_new = new_docs + modified_docs
    chunks = chunk_documents(all_new)
    embeddings = embed_chunks(chunks)
    vector_store.add(chunks, embeddings)
```

---

### Q25. How does RAG relate to your hackathon project?

**A:** Our hackathon project IS a RAG system! Here's the mapping:

| RAG Component | Our Implementation |
|---------------|-------------------|
| **Document loading** | Manual text via `/ingest` API |
| **Chunking** | `RecursiveCharacterTextSplitter(300, 50)` |
| **Embedding** | `GoogleGenerativeAIEmbeddings(gemini-embedding-001)` |
| **Vector store** | `chunks_store` (in-memory list) |
| **Retrieval** | Manual cosine similarity, top-3 |
| **Prompt** | Role + grounding + context + question |
| **Generation** | `ChatGoogleGenerativeAI` with `temperature=0` |
| **Source citation** | `used_extracts` → source mapping |
| **Fallback** | "Sorry, I could not find..." message |

**What makes it "naive RAG":**
- In-memory store (not persistent).
- Brute-force cosine similarity (not indexed).
- No re-ranking, no hybrid search.
- No query rewriting.
- Single-turn (no conversation memory).

---

> **💡 Viva Tip:** RAG is the **most important topic** for your hackathon viva since your project is a RAG system. Be able to explain every step of the pipeline, discuss failure modes, and propose improvements (hybrid search, re-ranking, persistent vector DB).

---

*End of Unit 9 — Retrieval Augmented Generation (RAG) 🔍*
