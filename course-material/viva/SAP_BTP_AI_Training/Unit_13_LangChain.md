# ⛓️ Unit 13 — LangChain

> **Module**: Module 5 — Agentic AI  
> **Duration**: Day 23–24 (16 hours)  
> **Dates**: 29-Jul-2026, 30-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — LangChain Core

### Q1. What is LangChain? What problems does it solve?

**A:** **LangChain** is the most widely-used open-source framework for building LLM-powered applications. It provides abstractions for every component of an AI pipeline.

**Problems it solves:**

| Problem | LangChain Solution |
|---------|-------------------|
| Different LLMs have different APIs | Unified `ChatModel` interface for GPT, Gemini, Claude |
| Prompt management is complex | `ChatPromptTemplate`, `PromptTemplate` |
| RAG requires many components | `Retriever`, `VectorStore`, `TextSplitter` |
| Agents need tool management | `Tool`, `AgentExecutor` |
| Chaining operations is verbose | LCEL pipe (`|`) operator |
| No conversation history | `ConversationBufferMemory`, message history |
| Debugging is hard | LangSmith integration |

---

### Q2. Explain LangChain's core abstractions.

**A:**

| Abstraction | What It Is | Example |
|------------|-----------|---------|
| **Chat Models** | Interface to LLM APIs | `ChatGoogleGenerativeAI`, `ChatOpenAI`, `ChatAnthropic` |
| **Prompts** | Template and manage prompts | `ChatPromptTemplate`, `FewShotPromptTemplate` |
| **Output Parsers** | Parse LLM text output into structured data | `StrOutputParser`, `JsonOutputParser`, `with_structured_output()` |
| **Retrievers** | Fetch relevant documents from a store | `VectorStoreRetriever`, `BM25Retriever` |
| **Vector Stores** | Store and search embeddings | `Chroma`, `FAISS`, `Pinecone` |
| **Document Loaders** | Load documents from various sources | `PyPDFLoader`, `TextLoader`, `WebBaseLoader` |
| **Text Splitters** | Split documents into chunks | `RecursiveCharacterTextSplitter` |
| **Memory** | Manage conversation history | `ConversationBufferMemory`, `ConversationSummaryMemory` |
| **Agents** | LLMs that use tools autonomously | `create_react_agent`, `create_openai_tools_agent` |
| **Tools** | Functions agents can call | `@tool` decorator, `DuckDuckGoSearchRun` |
| **Chains** | Composed sequences of operations | LCEL chains |

---

### Q3. What is LCEL (LangChain Expression Language)?

**A:** **LCEL** is a declarative way to compose chains using the `|` (pipe) operator. It automatically handles streaming, async, batching, and tracing.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
parser = StrOutputParser()

# Simple chain: prompt | llm | parser
chain = (
    ChatPromptTemplate.from_template("Summarize this in one sentence: {text}")
    | llm
    | parser
)

result = chain.invoke({"text": "LangChain is a framework for building LLM applications..."})
# "LangChain provides abstractions for building LLM-powered applications."

# Batch: run on many inputs
results = chain.batch([{"text": doc} for doc in documents])

# Stream: get output token by token
for chunk in chain.stream({"text": long_text}):
    print(chunk, end="", flush=True)

# Async
result = await chain.ainvoke({"text": text})
```

**Key `Runnable` interface** — every LangChain component implements: `invoke`, `batch`, `stream`, `ainvoke`, `astream`.

---

### Q4. What is `RunnablePassthrough` and `RunnableParallel`?

**A:**

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# RunnablePassthrough: Pass input through unchanged (often used in RAG)
chain = {
    "context": retriever,              # Retrieved docs
    "question": RunnablePassthrough()  # Original question unchanged
} | prompt | llm

# Example:
chain.invoke("How many leaves?")
# "context" gets retrieved documents
# "question" gets "How many leaves?" unchanged

# RunnableParallel: Run multiple operations at the same time
parallel = RunnableParallel(
    sentiment=sentiment_chain,
    topics=topic_chain,
    summary=summary_chain
)
result = parallel.invoke({"text": article})
# Returns:
# {
#   "sentiment": "positive",
#   "topics": ["AI", "cloud"],
#   "summary": "Article discusses..."
# }
```

---

### Q5. Explain ChatPromptTemplate in detail.

**A:**

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Method 1: From messages list
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {domain} assistant."),
    ("human", "{question}")
])

# Method 2: From template string
prompt = ChatPromptTemplate.from_template("Answer this {domain} question: {question}")

# Method 3: With conversation history placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),   # Inject conversation history here
    ("human", "{question}")
])

# Invoke to see the formatted messages:
messages = prompt.format_messages(
    domain="HR",
    question="How many leaves do I get?",
    history=[HumanMessage(content="Hello"), AIMessage(content="Hi there!")]
)
```

---

### Q6. How does LangChain handle output parsing?

**A:**

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

# StrOutputParser: Extract text content from ChatMessage
parser = StrOutputParser()
chain = prompt | llm | parser
result = chain.invoke({"q": "..."})  # Returns plain string

# JsonOutputParser: Parse JSON output
class Analysis(BaseModel):
    sentiment: str
    score: float
    topics: list[str]

parser = JsonOutputParser(pydantic_object=Analysis)
# Automatically adds format instructions to the prompt
chain = prompt | llm | parser

# with_structured_output (most powerful): Uses function calling under the hood
class GroundedAnswer(BaseModel):
    answer: str
    used_extracts: list[int] = []

result = llm.with_structured_output(GroundedAnswer).invoke(prompt)
# Guaranteed to return a GroundedAnswer object (or raise validation error)
```

---

## 🔹 Section 2 — LangChain RAG

### Q7. How do you build a complete RAG pipeline with LangChain?

**A:**

```python
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# === INDEXING PHASE ===
# 1. Load documents
loader = TextLoader("hr_policy.txt")
docs = loader.load()

# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 3. Embed and store
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

# === QUERYING PHASE ===
# 4. Create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# 5. Define RAG prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer using ONLY the context below.
                  If not in context, say 'Information not available in documents.'
                  Context: {context}"""),
    ("human", "{question}")
])

# 6. Build RAG chain
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def format_docs(docs):
    return "\n\n".join([f"[Source: {d.metadata['source']}]\n{d.page_content}" for d in docs])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("How many annual leaves do I get?")
```

---

### Q8. What is LangChain's Retriever interface?

**A:** A **Retriever** is LangChain's abstraction for any component that takes a query string and returns relevant documents.

```python
# Vector store retriever
retriever = vector_store.as_retriever(
    search_type="similarity",           # "similarity", "mmr", "similarity_score_threshold"
    search_kwargs={"k": 5}              # Return top 5
)

# MMR (Maximal Marginal Relevance): Balances relevance with diversity
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
)
# Fetches 20 candidates, returns 5 that are both relevant AND diverse

# Score threshold: Only return docs above a relevance threshold
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.7}
)

# MultiQueryRetriever: Generate multiple query variations
from langchain.retrievers import MultiQueryRetriever
retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm
)
# Generates 5 query variants, retrieves for each, deduplicates results
```

---

## 🔹 Section 3 — LangChain Agents

### Q9. How do you create a LangChain agent?

**A:**

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool, DuckDuckGoSearchRun

# Define tools
search = DuckDuckGoSearchRun()

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Input: valid Python math expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

tools = [search, calculator]

# Create agent prompt
from langchain import hub
prompt = hub.pull("hwchase17/react")  # Standard ReAct prompt

# Create agent
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
agent = create_react_agent(llm, tools, prompt)

# Create executor (manages the loop)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,          # Show thought/action/observation
    max_iterations=10,     # Stop after 10 iterations
    handle_parsing_errors=True  # Don't crash on parse errors
)

result = executor.invoke({"input": "What is 15% of Apple's current market cap?"})
print(result["output"])
```

---

### Q10. What types of agents does LangChain support?

**A:**

| Agent Type | How It Works | Best For |
|-----------|-------------|----------|
| **ReAct** | Reason-Act loop with text-based tool calls | General purpose, transparent reasoning |
| **OpenAI Functions/Tools** | Uses native function calling | More reliable tool invocation |
| **Structured Chat** | Multi-input tools with structured JSON | Tools with complex inputs |
| **Conversational ReAct** | ReAct with conversation history | Chatbot-style agents |
| **Self-Ask with Search** | Breaks into sub-questions | Complex factual queries |

```python
# Modern approach: OpenAI-tools agent (works with any tool-calling model)
from langchain.agents import create_tool_calling_agent

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
```

---

## 🔹 Section 4 — LangChain Memory

### Q11. How does memory work in LangChain?

**A:**

```python
from langchain.memory import (
    ConversationBufferMemory,         # Store all messages
    ConversationBufferWindowMemory,   # Store last K messages
    ConversationSummaryMemory,        # Store LLM-generated summary
    ConversationSummaryBufferMemory   # Summary + recent messages
)

# Buffer Memory: Keep all messages
memory = ConversationBufferMemory(return_messages=True)

# Window Memory: Keep last 5 exchanges
memory = ConversationBufferWindowMemory(k=5, return_messages=True)

# Summary Memory: Compress history into a summary (use LLM)
memory = ConversationSummaryMemory(llm=llm, return_messages=True)

# Modern approach: RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history"
)

# Session 1, Turn 1
with_history.invoke(
    {"question": "My name is Rudra"},
    config={"configurable": {"session_id": "user123"}}
)
# Session 1, Turn 2
with_history.invoke(
    {"question": "What's my name?"},
    config={"configurable": {"session_id": "user123"}}
)
# Returns: "Your name is Rudra."
```

---

### Q12. What is the difference between ConversationBufferMemory and ConversationSummaryMemory?

**A:**

| Memory Type | How It Stores | Token Cost | Accuracy | Use Case |
|------------|--------------|------------|---------|----------|
| **Buffer** | Every message verbatim | Grows unboundedly | Perfect | Short conversations |
| **Window** | Last K messages only | Fixed limit | Loses older context | Medium conversations |
| **Summary** | LLM-compressed summary | Small + grows slowly | May lose details | Long conversations |
| **Summary Buffer** | Summary + recent messages | Bounded | Good balance | Production chatbots |

---

## 🔹 Section 5 — LangChain Integrations

### Q13. What are LangChain Document Loaders?

**A:**

```python
# Text files
from langchain_community.document_loaders import TextLoader
docs = TextLoader("policy.txt").load()

# PDFs
from langchain_community.document_loaders import PyPDFLoader
docs = PyPDFLoader("manual.pdf").load()  # One Document per page

# Web pages
from langchain_community.document_loaders import WebBaseLoader
docs = WebBaseLoader("https://example.com/docs").load()

# Directory of files
from langchain_community.document_loaders import DirectoryLoader
docs = DirectoryLoader("./docs/", glob="**/*.txt").load()

# CSV
from langchain_community.document_loaders import CSVLoader
docs = CSVLoader("employees.csv").load()  # One Document per row

# YouTube video transcripts
from langchain_community.document_loaders import YoutubeLoader
docs = YoutubeLoader.from_youtube_url("https://youtube.com/watch?v=...").load()
```

---

### Q14. What are the vector stores available in LangChain?

**A:**

```python
# ChromaDB (open source, runs locally)
from langchain_community.vectorstores import Chroma
vector_store = Chroma.from_documents(docs, embeddings, persist_directory="./db")

# FAISS (Meta, in-memory, fast)
from langchain_community.vectorstores import FAISS
vector_store = FAISS.from_documents(docs, embeddings)
vector_store.save_local("faiss_index")  # Save to disk

# Pinecone (cloud, managed)
from langchain_pinecone import PineconeVectorStore
vector_store = PineconeVectorStore.from_documents(docs, embeddings, index_name="my-index")

# SAP HANA Cloud Vector Engine
from langchain_community.vectorstores import HanaDB
vector_store = HanaDB(connection=conn, embedding=embeddings, table_name="DOCS")
```

---

### Q15. What is LangSmith? Why is it important?

**A:** **LangSmith** is LangChain's observability and debugging platform. It traces every step of your LangChain application.

**What it captures:**
- Every LLM call (input prompt, output, latency, cost).
- Every tool call (input arguments, output).
- Chain execution flow.
- Errors and exceptions.

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_key"
os.environ["LANGCHAIN_PROJECT"] = "my-rag-project"

# All subsequent LangChain calls are automatically traced!
result = rag_chain.invoke("How many leaves?")
# → LangSmith shows the full trace: which chunks were retrieved, exact prompt sent, LLM response
```

---

## 🔹 Section 6 — Quick Fire Questions

### Q16. What is the difference between `Document` and `str` in LangChain?

**A:**
- **`str`** — Raw text string.
- **`Document`** — LangChain object with `page_content` (str) + `metadata` (dict).

```python
from langchain_core.documents import Document

doc = Document(
    page_content="Annual leave is 18 days per year.",
    metadata={"source": "hr_policy.txt", "page": 3, "section": "Leave Policy"}
)
```

Metadata is used for source attribution, filtering, and debugging.

---

### Q17. What is `invoke` vs `run` vs `call` in LangChain?

**A:** These are different historical interfaces:
- **`invoke`** (current, LCEL) — Accepts dict/str, returns dict/str. The modern standard.
- **`run`** (legacy) — Simpler string input/output. Deprecated.
- **`__call__`** (legacy) — Called as a function. Deprecated.

Always use `invoke` (or `ainvoke`, `stream`, `astream`, `batch`) in modern LangChain.

---

### Q18. What is the `hub` in LangChain?

**A:** **LangChain Hub** is a collection of shared, community-contributed prompts.

```python
from langchain import hub

# Pull a pre-built prompt (e.g., standard ReAct agent prompt)
prompt = hub.pull("hwchase17/react")

# Push your own prompt
hub.push("your-username/my-rag-prompt", my_prompt)
```

---

### Q19. What is `@chain` decorator?

**A:** The `@chain` decorator converts a Python function into a `Runnable` that works in LCEL pipelines:

```python
from langchain_core.runnables import chain

@chain
def format_context(docs: list) -> str:
    """Custom document formatting function — now usable in LCEL chains."""
    return "\n\n".join([
        f"[Doc {i+1}] {doc.page_content}" for i, doc in enumerate(docs)
    ])

rag_chain = {"context": retriever | format_context, "question": RunnablePassthrough()} | prompt | llm
```

---

### Q20. What is `with_config()` in LangChain?

**A:** `with_config()` lets you override configuration (like tags, metadata, callbacks) at runtime:

```python
chain = prompt | llm

# Add tags for tracing
chain.with_config({"tags": ["production", "user-123"]}).invoke({"question": "..."})

# Set recursion limit
chain.with_config({"recursion_limit": 5}).invoke({...})
```

---

> **💡 Viva Tip:** LangChain is the framework you used in your hackathon project. Be very comfortable explaining `ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`, `RecursiveCharacterTextSplitter`, and `with_structured_output`. These are all LangChain components!

---

*End of Unit 13 — LangChain ⛓️*
