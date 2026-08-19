# 🛠️ Unit 8 — GenAI Tools

> **Module**: Module 4 — Generative AI  
> **Duration**: Day 15 (8 hours)  
> **Date**: 17-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — GenAI Tools Landscape

### Q1. What are GenAI tools? Categorize the main types.

**A:** GenAI tools are software products and platforms that leverage generative AI models for specific tasks.

| Category | Tools | What They Do |
|----------|-------|-------------|
| **Chat/Assistants** | ChatGPT, Gemini, Claude, Perplexity | General conversation, Q&A, reasoning |
| **Code Assistants** | GitHub Copilot, Cursor, Codeium, Amazon Q | Code generation, completion, debugging |
| **Image Generation** | DALL-E, Midjourney, Stable Diffusion, Firefly | Create images from text prompts |
| **Document/Knowledge** | NotebookLM, ChatPDF, Notion AI | Summarize, query, organize documents |
| **Writing** | Jasper, Copy.ai, Grammarly AI | Marketing copy, editing, content |
| **Video** | Sora, Runway, Synthesia | Generate or edit video |
| **Audio** | ElevenLabs, Murf, Descript | Voice synthesis, transcription |
| **Development Frameworks** | LangChain, LlamaIndex, Semantic Kernel | Build GenAI applications |
| **Enterprise AI** | SAP Joule, Microsoft Copilot, Salesforce Einstein | AI in business workflows |

---

### Q2. What is ChatGPT? How does it work?

**A:** **ChatGPT** is OpenAI's conversational AI product built on the GPT (Generative Pre-trained Transformer) model family.

**How it works:**
1. User sends a message (prompt).
2. ChatGPT tokenizes the input.
3. Processes through the transformer model (billions of parameters).
4. Generates response token by token (autoregressive).
5. Returns the complete response.

**Capabilities:** Text generation, summarization, translation, code writing, reasoning, math, creative writing, data analysis (with Code Interpreter).

**Versions:**
| Version | Model | Key Feature |
|---------|-------|------------|
| ChatGPT Free | GPT-3.5 / GPT-4o mini | Free, basic |
| ChatGPT Plus | GPT-4o | Multimodal, advanced reasoning |
| ChatGPT Enterprise | GPT-4o | Data privacy, admin controls |

---

### Q3. What is Google Gemini? How does it differ from ChatGPT?

**A:** **Gemini** is Google DeepMind's multimodal AI model family, natively designed to handle text, images, audio, video, and code.

| Aspect | ChatGPT (GPT-4o) | Gemini |
|--------|------------------|--------|
| Company | OpenAI | Google DeepMind |
| Multimodal | Added later | Native from start |
| Context window | 128K tokens | Up to 1M tokens |
| Search integration | Web browsing plugin | Deep Google Search integration |
| Code execution | Code Interpreter | Google Colab integration |
| Enterprise | OpenAI API | Google Cloud, SAP GenAI Hub |
| Open variants | No | Gemma (open source) |

**Gemini variants:**
- **Gemini Nano** — On-device (mobile, edge).
- **Gemini Flash** — Fast and cost-effective.
- **Gemini Pro** — Balanced performance.
- **Gemini Ultra** — Most capable (complex reasoning).

---

### Q4. What is LangChain? Why is it important for GenAI development?

**A:** **LangChain** is the most popular Python framework for building applications powered by LLMs.

**Key components:**

| Component | Purpose | Example |
|-----------|---------|---------|
| **Chat Models** | Interface to LLMs | `ChatGoogleGenerativeAI`, `ChatOpenAI` |
| **Prompts** | Template and manage prompts | `ChatPromptTemplate`, `PromptTemplate` |
| **Chains** | Sequence of operations | Prompt → LLM → Parser |
| **Agents** | LLMs that decide which tools to use | ReAct agent with search + calculator |
| **Memory** | Conversation history | `ConversationBufferMemory` |
| **Retrievers** | Fetch relevant documents | Vector store retriever for RAG |
| **Output Parsers** | Structure LLM output | `with_structured_output()`, JSON parser |
| **Tools** | External capabilities for agents | Web search, code execution, APIs |

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
prompt = ChatPromptTemplate.from_template("Explain {topic} in simple terms")
chain = prompt | llm  # LCEL (LangChain Expression Language)
response = chain.invoke({"topic": "quantum computing"})
```

---

### Q5. What is LlamaIndex? How does it compare to LangChain?

**A:** **LlamaIndex** is a data framework for building LLM applications focused on **data ingestion and retrieval** (RAG).

| Aspect | LangChain | LlamaIndex |
|--------|-----------|------------|
| **Focus** | General LLM application framework | Data indexing and retrieval (RAG) |
| **Strength** | Agents, chains, tool integration | Document loading, indexing, querying |
| **RAG** | Supported (but manual setup) | Primary focus (built-in RAG pipeline) |
| **Agents** | Strong (ReAct, tool-based) | Basic agent support |
| **Learning curve** | Steeper | Simpler for RAG tasks |
| **Use together?** | ✅ Yes — often used together | ✅ Yes |

```python
# LlamaIndex RAG in 5 lines:
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data/").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is the leave policy?")
```

---

### Q6. What are vector databases? Name the popular ones.

**A:** **Vector databases** are specialized databases designed to store, index, and query **vector embeddings** efficiently.

| Database | Type | Key Feature | Use Case |
|----------|------|-------------|----------|
| **ChromaDB** | Open-source | Simple, Python-native | Prototyping, small-scale RAG |
| **Pinecone** | Cloud-managed | Fully managed, scalable | Production RAG applications |
| **Weaviate** | Open-source | Hybrid search (vector + keyword) | Enterprise search |
| **FAISS** | Library (Meta) | Fast similarity search, not a DB | Offline/batch processing |
| **Milvus** | Open-source | Highly scalable | Large-scale production |
| **Qdrant** | Open-source | Rust-based, fast | Performance-critical apps |
| **SAP HANA Cloud Vector Engine** | SAP | Integrated with SAP ecosystem | SAP-based RAG applications |

**Why vector DBs exist:** Regular databases can't efficiently find "semantically similar" items. Vector DBs use specialized indexes (HNSW, IVF) for O(log N) similarity search instead of O(N) brute force.

---

### Q7. What are AI orchestration tools?

**A:** **AI orchestration** tools manage complex AI workflows involving multiple models, tools, and steps.

| Tool | What It Does |
|------|-------------|
| **LangChain** | Chain LLM calls, tools, and logic |
| **LangGraph** | Stateful, graph-based agent workflows |
| **Semantic Kernel** (Microsoft) | Orchestrate AI plugins and planners |
| **CrewAI** | Multi-agent collaboration framework |
| **AutoGen** (Microsoft) | Multi-agent conversations |
| **SAP AI Core Orchestration** | Orchestrate AI workflows in SAP ecosystem |

---

### Q8. What is Hugging Face? Why is it important?

**A:** **Hugging Face** is the GitHub of AI — a platform for sharing, discovering, and deploying ML models.

**Key offerings:**
- **Model Hub** — 500K+ pre-trained models (LLMs, vision, audio).
- **Datasets Hub** — 100K+ datasets for training/evaluation.
- **Transformers library** — Python library to use any model in 3 lines of code.
- **Spaces** — Host ML demos and apps.
- **Inference API** — Run models via API without managing infrastructure.

```python
from transformers import pipeline

# Sentiment analysis in 2 lines:
classifier = pipeline("sentiment-analysis")
result = classifier("This product is amazing!")
# [{'label': 'POSITIVE', 'score': 0.9998}]
```

---

## 🔹 Section 2 — Practical GenAI Tools

### Q9. What is Streamlit? How is it used with GenAI?

**A:** **Streamlit** is a Python framework for building interactive web apps quickly — perfect for GenAI demos and prototypes.

```python
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

st.title("📋 Document Q&A")

question = st.text_input("Ask a question:")
if question:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    response = llm.invoke(question)
    st.write(response.content)
```

**Run:** `streamlit run app.py` → Opens a web UI at `localhost:8501`.

---

### Q10. What is Gradio? How does it compare to Streamlit?

**A:** **Gradio** is another Python library for building ML/AI demos, focused on creating interfaces for models.

| Aspect | Streamlit | Gradio |
|--------|-----------|--------|
| Focus | General data apps | ML model interfaces |
| Sharing | Self-hosted | Free public URL sharing |
| Customization | More flexible | Simpler, more constrained |
| Hugging Face | No native integration | Built-in Spaces integration |
| Best for | Full applications | Quick model demos |

---

### Q11. What tools are used for evaluating LLM outputs?

**A:**

| Tool | What It Evaluates |
|------|-------------------|
| **RAGAS** | RAG pipeline quality (faithfulness, relevance, recall) |
| **DeepEval** | LLM output quality (hallucination, bias, toxicity) |
| **LangSmith** | LangChain traces, debugging, evaluation |
| **Weights & Biases** | Experiment tracking, model comparison |
| **Human evaluation** | Manual review of outputs |

**RAGAS metrics for RAG:**
- **Faithfulness** — Is the answer faithful to the retrieved context?
- **Answer relevancy** — Does the answer actually address the question?
- **Context precision** — Are the retrieved documents relevant?
- **Context recall** — Are all relevant documents retrieved?

---

## 🔹 Section 3 — GenAI Development Patterns

### Q12. What is the typical architecture of a GenAI application?

**A:**

```
[User Interface]
  Streamlit / React / FastAPI
        ↓
[Application Layer]
  LangChain / LlamaIndex
  - Prompt management
  - Chain orchestration
  - Memory management
        ↓
[Retrieval Layer]     [Model Layer]
  Vector DB           LLM API
  (ChromaDB,          (Gemini, GPT,
   HANA Vector)        Claude)
        ↓
[Data Layer]
  Documents, databases,
  APIs, files
```

---

### Q13. What is LCEL (LangChain Expression Language)?

**A:** **LCEL** is LangChain's declarative syntax for composing chains using the pipe (`|`) operator.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LCEL chain: prompt → model → parser
chain = (
    ChatPromptTemplate.from_template("Tell me a joke about {topic}")
    | ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    | StrOutputParser()
)

result = chain.invoke({"topic": "programming"})

# With multiple steps:
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | output_parser
)
```

**Benefits:** Readable, composable, supports streaming, async, and batch operations natively.

---

### Q14. What is semantic search vs keyword search?

**A:**

| Aspect | Keyword Search | Semantic Search |
|--------|---------------|-----------------|
| **How it works** | Exact word matching | Meaning-based matching via embeddings |
| **"vacation days"** | Only finds docs with exact phrase | Also finds "annual leave", "PTO", "time off" |
| **Technology** | Full-text search (Elasticsearch, SQL LIKE) | Embeddings + vector similarity |
| **Pros** | Fast, predictable | Understands synonyms, context |
| **Cons** | Misses semantic matches | Slower, needs embedding model |
| **Best approach** | Combine both! | **Hybrid search** = keyword + semantic |

---

### Q15. What is a model gateway / model router?

**A:** A **model gateway** is a layer that routes requests to different LLMs based on requirements (cost, capability, latency).

```python
def route_to_model(query, complexity):
    if complexity == "simple":
        return gemini_flash(query)       # Cheap, fast
    elif complexity == "medium":
        return gemini_pro(query)         # Balanced
    else:
        return gpt4(query)              # Most capable, expensive
```

**SAP GenAI Hub** acts as a model gateway — provides unified access to multiple LLM providers (Google, OpenAI, Meta) through a single API.

---

## 🔹 Section 4 — Quick Fire Questions

### Q16. What is a tokenizer?

**A:** A **tokenizer** converts text into tokens (subword units) that the model can process, and vice versa. Different models use different tokenizers (BPE, SentencePiece, WordPiece).

---

### Q17. What is model context protocol (MCP)?

**A:** **MCP** is a standardized protocol for connecting AI models to external data sources and tools. It provides a universal way for LLMs to access databases, APIs, and file systems.

---

### Q18. What is function calling / tool use in LLMs?

**A:** **Function calling** allows LLMs to generate structured arguments to call external functions/tools, enabling them to interact with the real world.

```python
# LLM decides: "I need to search for weather data"
# Returns: {"function": "get_weather", "arguments": {"city": "Mumbai"}}
# Your code executes: get_weather("Mumbai")
# Result fed back to LLM for final answer
```

This is how `with_structured_output()` works — the LLM "calls a function" that matches the Pydantic schema.

---

### Q19. What is the difference between synchronous and streaming LLM responses?

**A:**
- **Synchronous:** Wait for the complete response → display all at once. Better for programmatic use.
- **Streaming:** Receive tokens as they're generated → display incrementally. Better for user-facing chat (feels faster).

```python
# Streaming in LangChain:
for chunk in llm.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

---

### Q20. What is a model card?

**A:** A **model card** is a document that describes an ML model's intended use, performance, limitations, and ethical considerations. Like a nutrition label for AI models. Hugging Face requires model cards for all published models.

---

> **💡 Viva Tip:** For GenAI tools, focus on understanding the **architecture** (how tools fit together) rather than memorizing every tool name. Know LangChain, vector databases, and the RAG pattern deeply — these are the most likely viva topics.

---

*End of Unit 8 — GenAI Tools 🛠️*
