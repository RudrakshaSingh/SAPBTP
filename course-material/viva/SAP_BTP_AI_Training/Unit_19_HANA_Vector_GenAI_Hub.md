# 🔷 Unit 19 — HANA Cloud Vector Engine + GenAI Hub

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 31 (8 hours)  
> **Date**: 08-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — HANA Cloud Vector Engine Fundamentals

### Q1. What is the SAP HANA Cloud Vector Engine?

**A:** The **HANA Cloud Vector Engine** is a built-in capability of SAP HANA Cloud that allows storing, indexing, and **similarity-searching over vector embeddings** — turning HANA Cloud into a native vector database.

**Why it's a game-changer for SAP customers:**
- No separate vector database needed (no ChromaDB, Pinecone, Weaviate).
- Embeddings stored **alongside** business data in the same HANA database.
- Combine vector similarity search with traditional SQL (JOIN, WHERE, GROUP BY).
- Enterprise features: backup, GDPR, access control, audit trails — inherited from HANA.
- Native integration with SAP GenAI Hub and SAP AI Core.

```
Before Vector Engine:
  HANA Cloud (business data) + ChromaDB (vectors) — two systems to manage

After Vector Engine:
  HANA Cloud (business data + vectors) — one system, one admin, one backup
```

---

### Q2. What data type is used for vectors in HANA Cloud?

**A:** HANA Cloud uses the **`REAL_VECTOR`** data type to store embedding vectors.

```sql
-- Create a table with an embedding column
CREATE TABLE "HR_POLICY_CHUNKS" (
    "ID"          INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "DOC_SOURCE"  NVARCHAR(500) NOT NULL,
    "CHUNK_TEXT"  NCLOB         NOT NULL,
    "CHUNK_IDX"   INTEGER,
    "CREATED_AT"  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    "EMBEDDING"   REAL_VECTOR(1536)  -- 1536 for OpenAI ada-002
);

-- For Google Gemini embeddings (768 dimensions):
"EMBEDDING"   REAL_VECTOR(768)

-- For text-embedding-3-large (3072 dimensions):
"EMBEDDING"   REAL_VECTOR(3072)
```

**Important:** You must specify the exact dimension count in the column definition — it must match your embedding model's output dimension.

---

### Q3. How do you insert vectors into HANA Cloud?

**A:**

```python
from hdbcli import dbapi
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
import json

# Connect to HANA Cloud
conn = dbapi.connect(
    address='your-instance.hanacloud.ondemand.com',
    port=443,
    user='DBADMIN',
    password='secret',
    encrypt=True
)

# Initialize embedding model (via GenAI Hub)
embeddings = init_embedding_model('text-embedding-ada-002')

def insert_chunk(source: str, chunk_text: str, chunk_idx: int):
    # 1. Generate embedding vector
    vector = embeddings.embed_documents([chunk_text])[0]  # List of 1536 floats

    # 2. Convert to HANA vector format
    vector_str = str(vector)  # "[0.023, -0.041, ...]"

    # 3. Insert into HANA
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO "HR_POLICY_CHUNKS" ("DOC_SOURCE", "CHUNK_TEXT", "CHUNK_IDX", "EMBEDDING")
        VALUES (?, ?, ?, TO_REAL_VECTOR(?))
    """, (source, chunk_text, chunk_idx, vector_str))
    conn.commit()
    print(f"Inserted chunk {chunk_idx} from {source}")
```

---

### Q4. How do you perform similarity search in HANA Cloud?

**A:**

```sql
-- Method 1: COSINE_SIMILARITY function
SELECT TOP 5
    "ID",
    "DOC_SOURCE",
    "CHUNK_TEXT",
    COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) AS "SIMILARITY_SCORE"
FROM "HR_POLICY_CHUNKS"
ORDER BY "SIMILARITY_SCORE" DESC;

-- Method 2: L2_DISTANCE (Euclidean)
SELECT TOP 5
    "CHUNK_TEXT",
    L2_DISTANCE("EMBEDDING", TO_REAL_VECTOR(?)) AS "DISTANCE"
FROM "HR_POLICY_CHUNKS"
ORDER BY "DISTANCE" ASC;

-- Method 3: DOT_PRODUCT (for normalized vectors)
SELECT TOP 5
    "CHUNK_TEXT",
    DOT_PRODUCT("EMBEDDING", TO_REAL_VECTOR(?)) AS "SIMILARITY"
FROM "HR_POLICY_CHUNKS"
ORDER BY "SIMILARITY" DESC;
```

```python
def semantic_search(question: str, top_k: int = 3) -> list[dict]:
    # Embed the query
    query_vector = embeddings.embed_query(question)
    query_vector_str = str(query_vector)

    # Search HANA
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP ?
            "ID",
            "DOC_SOURCE",
            "CHUNK_TEXT",
            COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) AS "SCORE"
        FROM "HR_POLICY_CHUNKS"
        ORDER BY "SCORE" DESC
    """, (top_k, query_vector_str))

    results = cursor.fetchall()
    return [
        {"id": r[0], "source": r[1], "text": r[2], "score": float(r[3])}
        for r in results
    ]

# Usage
docs = semantic_search("How many annual leaves do I get?", top_k=3)
for doc in docs:
    print(f"Score: {doc['score']:.4f} | Source: {doc['source']}")
    print(f"Text: {doc['text'][:100]}...")
```

---

### Q5. How is vector search in HANA different from a simple `LIKE` query?

**A:**

```sql
-- LIKE (keyword match): Only finds exact keyword matches
SELECT * FROM "HR_POLICY_CHUNKS"
WHERE "CHUNK_TEXT" LIKE '%annual leave%';
-- ❌ Misses: "vacation days", "PTO", "paid time off", "leave entitlement"

-- COSINE_SIMILARITY (semantic match): Understands meaning
SELECT TOP 3 "CHUNK_TEXT"
FROM "HR_POLICY_CHUNKS"
ORDER BY COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) DESC;
-- ✅ Finds: "annual leave", "vacation days", "PTO", "leave entitlement"
--          all have similar embeddings → high similarity score
```

**The power of vector search:**
- A user types "how many days off can I take" → semantic search finds chunks about "annual leave policy" even though no word matches.
- Traditional search would return nothing for "days off".

---

### Q6. How do you combine vector search with SQL filters (Hybrid RAG)?

**A:** HANA Cloud can combine vector similarity with SQL filters in one query:

```sql
-- Hybrid: Semantic similarity + SQL filter
-- "Find documents about leave policy for employees in India"
SELECT TOP 3
    "CHUNK_TEXT",
    "DOC_SOURCE",
    COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) AS "SCORE"
FROM "HR_POLICY_CHUNKS"
WHERE "COUNTRY" = 'India'           -- SQL filter: only India docs
  AND "DOC_TYPE" = 'hr_policy'      -- SQL filter: only policy docs
  AND "ACTIVE" = TRUE               -- SQL filter: only active docs
ORDER BY "SCORE" DESC;

-- Hybrid: Semantic + Keyword (combine scores)
SELECT TOP 5
    "CHUNK_TEXT",
    COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) * 0.7
        + SCORE() * 0.3  AS "COMBINED_SCORE"  -- 70% semantic + 30% keyword
FROM "HR_POLICY_CHUNKS"
    CONTAINS ("CHUNK_TEXT", ?, FUZZY(0.8))   -- SAP full-text search
ORDER BY "COMBINED_SCORE" DESC;
```

This **hybrid search** is more powerful than pure vector search:
- Vector search finds semantically relevant chunks.
- SQL filters remove irrelevant documents (wrong country, wrong doc type, outdated).
- Keyword search ensures exact terms (product codes, names) are matched.

---

## 🔹 Section 2 — Full RAG Pipeline with HANA Vector + GenAI Hub

### Q7. Build a complete SAP-native RAG system step by step.

**A:**

**Step 1: Create the database schema**
```sql
-- Run in HANA Cloud Database Explorer
CREATE TABLE "RAG_DOCUMENTS" (
    "ID"        INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "SOURCE"    NVARCHAR(500),
    "CATEGORY"  NVARCHAR(100),
    "CONTENT"   NCLOB,
    "CHUNK_IDX" INTEGER,
    "EMBEDDING" REAL_VECTOR(1536),
    "CREATED"   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a full-text index for hybrid search
CREATE FULLTEXT INDEX "FT_IDX_RAG" ON "RAG_DOCUMENTS" ("CONTENT");
```

**Step 2: Build the ingestion pipeline**
```python
from hdbcli import dbapi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model

conn = dbapi.connect(...)
embeddings = init_embedding_model('text-embedding-ada-002')
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def ingest_document(text: str, source: str, category: str = "general"):
    # Split
    chunks = splitter.split_text(text)
    print(f"Processing {len(chunks)} chunks from {source}")

    # Embed all chunks at once (batch for efficiency)
    vectors = embeddings.embed_documents(chunks)

    # Batch insert
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO "RAG_DOCUMENTS" ("SOURCE", "CATEGORY", "CONTENT", "CHUNK_IDX", "EMBEDDING")
        VALUES (?, ?, ?, ?, TO_REAL_VECTOR(?))
    """, [
        (source, category, chunk, i, str(vector))
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    ])
    conn.commit()
    print(f"✅ Ingested {len(chunks)} chunks from {source}")
```

**Step 3: Build the query pipeline**
```python
from gen_ai_hub.proxy.langchain.init_models import init_llm
from pydantic import BaseModel

llm = init_llm('gpt-4o', temperature=0, max_tokens=800)

class GroundedAnswer(BaseModel):
    answer: str
    sources: list[str]

def answer_question(question: str, category: str = None) -> GroundedAnswer:
    # Embed query
    query_vector = embeddings.embed_query(question)

    # Search HANA (with optional category filter)
    cursor = conn.cursor()
    filter_clause = "AND \"CATEGORY\" = ?" if category else ""
    params = [3, str(query_vector)]
    if category:
        params.append(category)

    cursor.execute(f"""
        SELECT TOP ?
            "SOURCE", "CONTENT",
            COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) AS "SCORE"
        FROM "RAG_DOCUMENTS"
        WHERE COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) > 0.6
        {filter_clause}
        ORDER BY "SCORE" DESC
    """, [3, str(query_vector), str(query_vector)] + ([category] if category else []))

    results = cursor.fetchall()
    if not results:
        return GroundedAnswer(
            answer="I could not find relevant information in the available documents.",
            sources=[]
        )

    # Build context
    context = "\n\n".join([
        f"[Source: {r[0]}]\n{r[1]}" for r in results
    ])
    sources = list(set([r[0] for r in results]))

    # Generate answer
    prompt = f"""You are an expert assistant. Answer using ONLY the context below.
If the answer is not in the context, say "Information not found in documents."

Context:
{context}

Question: {question}"""

    response = llm.with_structured_output(GroundedAnswer).invoke(prompt)
    return response

# Test
result = answer_question("How many annual leaves do I get?", category="hr_policy")
print(f"Answer: {result.answer}")
print(f"Sources: {result.sources}")
```

---

### Q8. How do you use LangChain's HanaDB vector store?

**A:** LangChain provides a native `HanaDB` integration:

```python
from langchain_community.vectorstores import HanaDB
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model, init_llm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from hdbcli import dbapi

# Connect
conn = dbapi.connect(...)
embeddings = init_embedding_model('text-embedding-ada-002')

# Create HanaDB vector store (auto-creates table if not exists)
vector_store = HanaDB(
    connection=conn,
    embedding=embeddings,
    table_name="LANGCHAIN_DOCS",  # HANA table name
    content_column="CHUNK_TEXT",
    metadata_column="METADATA",
    vector_column="EMBEDDING"
)

# Index documents (splitting + embedding + storage in one call)
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

loader = TextLoader("hr_policy.txt")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

vector_store.add_documents(chunks)
print(f"Indexed {len(chunks)} chunks in HANA Cloud!")

# Similarity search
similar_docs = vector_store.similarity_search(
    "How many annual leaves?",
    k=3,
    filter={"source": "hr_policy.txt"}
)

# Similarity search with scores
docs_with_scores = vector_store.similarity_search_with_score(
    "leave policy", k=5
)
for doc, score in docs_with_scores:
    print(f"Score: {score:.4f} | {doc.page_content[:100]}")

# As LangChain retriever (plugs into RAG chains)
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Full LCEL RAG chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template("""
Answer using only this context:
{context}

Question: {question}
""")

chain = (
    {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)),
     "question": RunnablePassthrough()}
    | prompt
    | init_llm('gpt-4o', temperature=0)
    | StrOutputParser()
)

answer = chain.invoke("How many leaves do I get?")
```

---

### Q9. What vector index does HANA Cloud support for fast similarity search?

**A:** HANA Cloud Vector Engine supports **HNSW (Hierarchical Navigable Small World)** indexing — the same algorithm used by production vector databases.

```sql
-- Create an HNSW index for fast approximate similarity search
CREATE VECTOR INDEX "IDX_RAG_EMBEDDING"
ON "RAG_DOCUMENTS" ("EMBEDDING")
USING HNSW
BUILD CONFIGURATION '{"MaxConnections": 16, "EfConstruction": 128}';
```

**Without index:** Brute-force scan — O(N) — compares query to EVERY vector.
**With HNSW index:** Approximate search — O(log N) — navigates a graph structure.

**HNSW parameters:**
- `MaxConnections` (M) — Graph connectivity. Higher = better quality but more memory. Default: 16.
- `EfConstruction` — Search scope during index building. Higher = better index quality but slower to build. Default: 128.

---

## 🔹 Section 3 — Advanced Vector Engine Features

### Q10. How do you delete and update vectors in HANA Cloud?

**A:**

```sql
-- Delete specific document chunks
DELETE FROM "RAG_DOCUMENTS"
WHERE "SOURCE" = 'old_policy.txt';

-- Update a chunk's text and regenerate embedding
-- (In practice: delete + re-insert, since REAL_VECTOR columns are immutable)
DELETE FROM "RAG_DOCUMENTS" WHERE "ID" = 42;
-- Then re-insert with new embedding
```

```python
def update_document(source: str, new_text: str, category: str):
    """Re-index a document by deleting old chunks and inserting new ones."""
    cursor = conn.cursor()

    # 1. Delete existing chunks for this document
    cursor.execute('DELETE FROM "RAG_DOCUMENTS" WHERE "SOURCE" = ?', (source,))
    deleted = cursor.rowcount
    print(f"Deleted {deleted} old chunks for {source}")

    # 2. Re-ingest with new content
    ingest_document(new_text, source, category)
    conn.commit()
```

---

### Q11. How do you monitor vector store quality?

**A:**

```sql
-- Check how many chunks per document
SELECT "SOURCE", COUNT(*) AS "CHUNK_COUNT"
FROM "RAG_DOCUMENTS"
GROUP BY "SOURCE"
ORDER BY "CHUNK_COUNT" DESC;

-- Check average similarity scores for a test query
-- (Run this periodically to detect embedding model drift)
SELECT
    AVG(COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?))) AS "AVG_SIM",
    MAX(COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?))) AS "MAX_SIM",
    MIN(COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?))) AS "MIN_SIM"
FROM "RAG_DOCUMENTS";

-- Check storage usage
SELECT
    TABLE_NAME,
    RECORD_COUNT,
    ALLOCATED_FIXED_PART_SIZE / 1024 / 1024 AS "SIZE_MB"
FROM M_CS_TABLES
WHERE TABLE_NAME = 'RAG_DOCUMENTS';
```

---

### Q12. What is the similarity score threshold? How do you use it?

**A:** A **similarity threshold** rejects retrieved chunks whose similarity score is below a cutoff — preventing the LLM from answering from irrelevant context.

```python
SIMILARITY_THRESHOLD = 0.65  # Tune this for your use case

def search_with_threshold(question: str, top_k: int = 5):
    query_vector = embeddings.embed_query(question)

    cursor.execute("""
        SELECT "SOURCE", "CONTENT",
            COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) AS "SCORE"
        FROM "RAG_DOCUMENTS"
        WHERE COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR(?)) > ?
        ORDER BY "SCORE" DESC
        LIMIT ?
    """, (str(query_vector), str(query_vector), SIMILARITY_THRESHOLD, top_k))

    results = cursor.fetchall()

    if not results:
        return None, "No relevant documents found above the similarity threshold."

    context = "\n\n".join([r[1] for r in results])
    return context, None
```

**How to calibrate threshold:**
- Test with questions that SHOULD be answerable → all should score > threshold.
- Test with out-of-scope questions → should NOT return results.
- Typically: 0.6-0.75 for most embedding models.

---

## 🔹 Section 4 — Quick Fire Questions

### Q13. What are the HANA Cloud vector functions?

**A:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `TO_REAL_VECTOR(string)` | Convert JSON array string to REAL_VECTOR | REAL_VECTOR |
| `TO_NVARCHAR(vector)` | Convert REAL_VECTOR to JSON string | NVARCHAR |
| `COSINE_SIMILARITY(v1, v2)` | Cosine similarity between two vectors | FLOAT (-1 to 1) |
| `L2_DISTANCE(v1, v2)` | Euclidean distance between two vectors | FLOAT (≥ 0) |
| `DOT_PRODUCT(v1, v2)` | Dot product of two vectors | FLOAT |
| `VECTOR_LENGTH(v)` | Number of dimensions | INTEGER |
| `VECTOR_NORM(v)` | L2 norm (magnitude) of the vector | FLOAT |

---

### Q14. What is the maximum vector dimension HANA Cloud supports?

**A:** As of 2026, HANA Cloud Vector Engine supports up to **65,000 dimensions** — more than sufficient for all current embedding models (max ~3,072 dimensions for OpenAI's largest model).

---

### Q15. Can HANA Vector Engine handle millions of documents?

**A:** Yes. With the HNSW index, HANA Cloud can handle:
- Millions of vectors with fast approximate nearest neighbor search.
- Enterprise-scale workloads (comparable to Pinecone, Weaviate).
- The HNSW index makes search O(log N) instead of O(N) brute force.

For very large scales (100M+ vectors), HANA Data Lake (columnar store) can supplement with batch similarity search.

---

### Q16. What is the difference between embedding at ingestion time vs query time?

**A:**

| | Ingestion Time | Query Time |
|-|---------------|-----------|
| **When** | Once, when document is added | Every user query |
| **Input** | Document chunks | User's question |
| **Output** | Stored in HANA REAL_VECTOR column | Used only for search |
| **Cost** | Amortized (paid once) | Per query (recurring) |
| **Batch?** | ✅ Yes — batch embed many chunks | ❌ No — single query at a time |

**Optimization:** Batch-embed chunks during ingestion (embed 100 chunks at once, not 1 by 1) — much faster and cheaper.

---

> **💡 Viva Tip:** The HANA Vector Engine question will likely be: "How would you upgrade your hackathon's in-memory vector store to production?" Answer: Replace the Python list + cosine similarity with `HanaDB` vector store → all embeddings persist in HANA Cloud → same `similarity_search()` API from LangChain. No change in application logic, just in the storage layer.

---

*End of Unit 19 — HANA Cloud Vector Engine + GenAI Hub 🔷*
