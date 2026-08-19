# 🤖 Unit 18 — SAP Business AI & GenAI Hub

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 30 (8 hours)  
> **Date**: 07-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — SAP Business AI Strategy

### Q1. What is SAP Business AI? What differentiates it from generic AI?

**A:** **SAP Business AI** is SAP's strategy to embed AI capabilities **directly into business processes** across all SAP products — not as standalone AI features, but as integrated, contextual intelligence.

**What makes SAP Business AI different:**

| Aspect | Generic AI (ChatGPT, etc.) | SAP Business AI |
|--------|---------------------------|-----------------|
| **Data** | General internet knowledge | Your specific SAP business data |
| **Context** | No business context | Understands SAP data models, processes |
| **Integration** | Separate tool | Embedded in SAP workflows |
| **Compliance** | Varies | GDPR, SOC2, enterprise-grade |
| **Output** | General text | Business actions (create PO, approve leave) |
| **Trust** | Hard to verify | Grounded in auditable business data |

**SAP's AI vision:** Every business process in SAP should be enhanced by AI — intelligently, relevantly, and responsibly.

---

### Q2. What are the three pillars of SAP Business AI?

**A:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAP BUSINESS AI                              │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  EMBEDDED AI    │  │  AI PLATFORM    │  │  GENERATIVE AI  │ │
│  │                 │  │                 │  │                 │ │
│  │ AI built into   │  │ SAP AI Core     │  │ SAP Joule       │ │
│  │ SAP products    │  │ SAP AI Launchpad│  │ GenAI Hub       │ │
│  │                 │  │                 │  │ SAP AI APIs     │ │
│  │ Ex: Smart pay   │  │ Train & deploy  │  │                 │ │
│  │ matching,       │  │ your own ML     │  │ LLM-powered     │ │
│  │ demand forecast │  │ models          │  │ experiences     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Pillar 1 — Embedded AI:** AI features already built into SAP products:
- **Cash Application** — Automatically matches incoming payments to invoices.
- **Demand Forecasting** — Predicts future inventory needs.
- **Contract Intelligence** — Extracts data from contracts using AI.

**Pillar 2 — AI Platform (SAP AI Core):** Infrastructure to build and deploy your own ML models on BTP.

**Pillar 3 — Generative AI (SAP Joule + GenAI Hub):** LLM-powered conversational and generative experiences across SAP.

---

### Q3. What are SAP's AI principles?

**A:** SAP follows three core principles for responsible AI:

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Relevant** | AI must be meaningful in business context | Grounded in SAP data, not generic |
| **Reliable** | AI must produce trustworthy, accurate outputs | Source attribution, hallucination prevention |
| **Responsible** | AI must be ethical, transparent, compliant | GDPR, audit trails, bias monitoring |

SAP published its **"AI Ethics Handbook"** committing to:
- No autonomous systems in safety-critical decisions.
- Human oversight for consequential AI actions.
- Transparency about when AI is being used.
- Data privacy — customer data never used to train SAP models.

---

### Q4. What is SAP AI Core?

**A:** **SAP AI Core** is a managed Kubernetes-based service on SAP BTP for the **full ML lifecycle** — from data preparation and training to model deployment and serving.

**Core concepts:**

| Concept | Description | Analogy |
|---------|-------------|---------|
| **Resource Group** | Isolated namespace for tenant's AI resources | Like a project in Google Cloud |
| **Scenario** | A collection of related AI use cases | Like a repository |
| **Executable** | A Docker image containing training/serving code | The AI "application" |
| **Training Job** | A run of the training executable on data | Like running a script |
| **Artifact** | Input/output data or model files in object storage | Model weights, datasets |
| **Configuration** | Parameters for an executable (hyperparameters) | Config file |
| **Deployment** | A live, running model serving endpoint | A deployed API |

```
Workflow:
1. Push Docker image with training code to container registry
2. Create Executable (register the image in AI Core)
3. Upload training data to Object Store (SAP HANA or S3)
4. Run Training Job (using the executable + data)
5. Save trained model as Artifact
6. Create Deployment (serve the model as REST API)
7. Call Deployment endpoint for predictions
```

---

### Q5. What is SAP AI Launchpad?

**A:** **SAP AI Launchpad** is the **web-based management UI** for SAP AI Core. It's where ML engineers and data scientists manage their AI workflows without writing code.

**What you can do in AI Launchpad:**

| Section | Functionality |
|---------|--------------|
| **Workspaces** | Connect to an AI Core instance |
| **ML Operations** | View scenarios, executables, configurations |
| **Training** | Start, monitor, and view training runs |
| **Models** | View registered model artifacts |
| **Deployments** | Create, start, stop, and test model endpoints |
| **GenAI Hub** | Configure and test foundation model access |
| **Orchestration** | Configure grounding, filtering, and model routing |

---

### Q6. What is SAP GenAI Hub?

**A:** **SAP GenAI Hub** is a service within SAP AI Core that provides **managed, secure access to multiple Large Language Models** through a unified API.

**Key value proposition:**
```
Without GenAI Hub:
  Your App → OpenAI API (OpenAI credentials, OpenAI compliance)
  Your App → Google Gemini API (Google credentials, Google compliance)
  Your App → Anthropic Claude API (Anthropic credentials)
  → Different SDKs, different auth, data goes to different providers

With GenAI Hub:
  Your App → SAP GenAI Hub API (SAP credentials, SAP compliance)
                    ├── Routes to OpenAI GPT-4o
                    ├── Routes to Google Gemini
                    └── Routes to Meta LLaMA
  → One API, one auth, data stays in SAP infrastructure
```

**Available models (as of 2026):**

| Provider | Models Available |
|----------|----------------|
| **OpenAI** | GPT-4o, GPT-4o mini, GPT-3.5 Turbo, text-embedding-ada-002, text-embedding-3 |
| **Google** | Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash, text-embedding-004 |
| **Meta** | LLaMA 3.1 70B, LLaMA 3.1 8B |
| **Mistral** | Mistral Large, Mistral 8x7B |
| **Anthropic** | Claude 3.5 Sonnet |
| **SAP** | SAP-trained domain-specific models |

---

### Q7. How do you set up and use SAP GenAI Hub programmatically?

**A:**

```bash
# Install the SAP GenAI Hub SDK
pip install generative-ai-hub-sdk
```

```python
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Set environment variables (from service key)
# AI_CORE_AUTH_URL, AI_CORE_CLIENT_ID, AI_CORE_CLIENT_SECRET,
# AI_CORE_BASE_URL, AI_CORE_RESOURCE_GROUP

# Initialize the proxy client
proxy_client = get_proxy_client('gen-ai-hub')

# Initialize LLM (LangChain-compatible)
llm = init_llm(
    'gpt-4o',
    proxy_client=proxy_client,
    max_tokens=1000,
    temperature=0
)

# Initialize embedding model
embeddings = init_embedding_model(
    'text-embedding-ada-002',
    proxy_client=proxy_client
)

# Use like any LangChain model
response = llm.invoke("Explain SAP BTP in simple terms")
print(response.content)

# Get embeddings
vectors = embeddings.embed_documents(["SAP HANA is an in-memory database"])
print(f"Embedding dimensions: {len(vectors[0])}")  # 1536 for ada-002

# Chat with message history
from langchain_core.messages import SystemMessage, HumanMessage
messages = [
    SystemMessage(content="You are an SAP expert assistant."),
    HumanMessage(content="What is the purpose of SAP BTP?")
]
response = llm.invoke(messages)
```

---

### Q8. What is a deployment in SAP AI Core / GenAI Hub?

**A:** A **deployment** in the context of GenAI Hub is a provisioned connection to a specific foundation model with specific configuration.

```
GenAI Hub Deployment:
  Deployment ID:   d-abc123
  Model:           gpt-4o
  Provider:        Azure OpenAI (via SAP)
  Region:          EU10 (for GDPR compliance)
  Status:          Running
  Created:         2026-08-01

Your code references this deployment ID, not the model directly:
  llm = init_llm('gpt-4o', deployment_id='d-abc123')
```

**Why deployment IDs matter:**
- You might have multiple GPT-4o deployments in different regions.
- AI Launchpad manages which deployments are active.
- Deployment IDs allow switching models without code changes.

---

### Q9. What is XSUAA? Why does it matter for SAP AI?

**A:** **XSUAA (Extended Services for User Account and Authentication)** is SAP BTP's authorization service — it handles authentication and role-based access control.

**How it works:**
```
1. User logs in → XSUAA issues a JWT access token
2. App validates token → Checks user's scopes/roles
3. AI service validates token → Verifies access to AI Core
4. Only authorized users can:
   - Call AI endpoints
   - Access sensitive business data
   - Use specific LLM models
```

**In practice for GenAI Hub:**
- Your application uses XSUAA client credentials to get a token.
- This token is passed to GenAI Hub API.
- GenAI Hub verifies you're authorized for the requested model/deployment.

```python
# Getting a token from XSUAA
import requests

token_response = requests.post(
    f"{AUTH_URL}/oauth/token",
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
)
access_token = token_response.json()["access_token"]

# Use token to call GenAI Hub
headers = {"Authorization": f"Bearer {access_token}"}
```

---

## 🔹 Section 2 — GenAI Hub in Practice

### Q10. How do you build a complete RAG application using GenAI Hub?

**A:**

```python
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel

# 1. Initialize models via GenAI Hub
llm = init_llm('gpt-4o', temperature=0, max_tokens=800)
embeddings = init_embedding_model('text-embedding-ada-002')

# 2. Set up vector store (ChromaDB for local; HANA Cloud in production)
vector_store = Chroma(embedding_function=embeddings, persist_directory="./chroma_db")

# 3. Ingest documents
def ingest_document(text: str, source: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    metadatas = [{"source": source, "chunk_idx": i} for i in range(len(chunks))]
    vector_store.add_texts(chunks, metadatas=metadatas)
    print(f"Ingested {len(chunks)} chunks from {source}")

# 4. Define structured output
class GroundedAnswer(BaseModel):
    answer: str
    sources_used: list[str]
    confidence: float

# 5. Build RAG chain
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant. Answer using ONLY the extracts below.
    If the answer is not in the extracts, say exactly:
    "I could not find information about this in the available documents."
    
    Extracts:
    {context}"""),
    ("human", "{question}")
])

def format_docs(docs):
    return "\n\n".join([
        f"[Extract {i+1} | Source: {d.metadata.get('source','Unknown')}]\n{d.page_content}"
        for i, d in enumerate(docs)
    ])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm.with_structured_output(GroundedAnswer)
)

# 6. Ask a question
result = rag_chain.invoke("How many annual leaves do employees get?")
print(f"Answer: {result.answer}")
print(f"Sources: {result.sources_used}")
print(f"Confidence: {result.confidence}")
```

---

### Q11. How does GenAI Hub handle model switching?

**A:** One of GenAI Hub's key features is **easy model switching** — swap models without changing application code.

```python
# Switch from GPT-4o to Gemini with ONE line change:
llm_gpt4 = init_llm('gpt-4o', temperature=0)
llm_gemini = init_llm('gemini-1.5-pro', temperature=0)

# Both expose identical LangChain interface
response_gpt = llm_gpt4.invoke(prompt)
response_gem = llm_gemini.invoke(prompt)

# A/B testing different models
import random
llm = llm_gpt4 if random.random() > 0.5 else llm_gemini
response = llm.invoke(prompt)
```

**Enterprise use case:** Run A/B tests to find which model is best for your specific business task, then switch the production model without code changes.

---

### Q12. What are the cost and rate limiting considerations for GenAI Hub?

**A:**

| Model | Input Cost (per 1K tokens) | Output Cost (per 1K tokens) |
|-------|---------------------------|------------------------------|
| GPT-4o | ~$0.005 | ~$0.015 |
| GPT-4o mini | ~$0.00015 | ~$0.0006 |
| Gemini 1.5 Flash | ~$0.0000375 | ~$0.00015 |
| Gemini 1.5 Pro | ~$0.00125 | ~$0.005 |

**Cost optimization strategies:**
- Use smaller models (Flash, mini) for simple tasks.
- Use larger models (Pro, GPT-4o) only for complex reasoning.
- Cache frequent responses.
- Reduce prompt length (token count).
- Use streaming to detect early termination opportunities.

**Rate limits in GenAI Hub:**
- Based on Requests Per Minute (RPM) and Tokens Per Minute (TPM).
- Handle with exponential backoff on `429` errors.
- GenAI Hub SDK handles basic retry logic automatically.

---

## 🔹 Section 3 — SAP AI Ecosystem

### Q13. What is SAP AI API?

**A:** **SAP AI API** is a catalog of pre-built AI APIs that SAP provides for common business AI tasks — without needing to build or train your own model.

| API | What It Does |
|-----|-------------|
| **Business Entity Recognition** | Extract entities (company, person, date, money) from text |
| **Document Information Extraction** | Parse invoices, purchase orders, payslips |
| **Document Classification** | Classify documents by type |
| **Recommendation** | Product/content recommendations |
| **Data Attribute Recommendation** | Complete missing data fields |
| **Language Detection** | Detect the language of text |
| **Translation** | Translate text (powered by SAP's multilingual models) |

---

### Q14. What is SAP Document Information Extraction (DOX)?

**A:** **DOX** extracts structured data from business documents using AI.

**Supported document types:**
- Purchase Orders (POs)
- Invoices
- Payment Advices
- Business Cards
- Bank Statements
- Payslips

```python
# Using DOX API
import requests

headers = {"Authorization": f"Bearer {access_token}"}

# Upload and process an invoice PDF
response = requests.post(
    f"{DOX_URL}/document/jobs",
    headers=headers,
    json={
        "value": base64_encoded_pdf,
        "filename": "invoice.pdf",
        "documentType": "invoice",
        "extractedFields": ["vendorName", "invoiceId", "totalAmount", "dueDate"]
    }
)

job_id = response.json()["id"]
# Poll for results...
result = requests.get(f"{DOX_URL}/document/jobs/{job_id}", headers=headers)
extracted = result.json()["extraction"]
print(f"Vendor: {extracted['vendorName']}")
print(f"Amount: {extracted['totalAmount']}")
```

---

### Q15. What is the difference between SAP AI Core and SAP AI Services?

**A:**

| Aspect | SAP AI Core | SAP AI Services |
|--------|------------|-----------------|
| **Purpose** | Build & deploy YOUR OWN models | Use SAP's PRE-BUILT AI APIs |
| **Model ownership** | You bring/train the model | SAP provides the model |
| **Customization** | Full (train on your data) | Limited (some fine-tuning) |
| **Setup** | Complex (Docker, pipelines) | Simple (REST API call) |
| **Use case** | Custom ML for unique business problems | Standard business AI tasks |
| **GenAI Hub** | Part of AI Core | Not applicable |

---

## 🔹 Section 4 — Quick Fire Questions

### Q16. What is the difference between a model and a deployment in GenAI Hub?

**A:**
- **Model:** The base LLM (e.g., `gpt-4o`) — the AI capability.
- **Deployment:** A provisioned, running instance of that model with specific config (region, quota, access) — identified by a deployment ID.

You reference deployments in code, not models directly. One model can have multiple deployments (e.g., EU region + US region).

---

### Q17. What is SAP's approach to AI compliance with GDPR?

**A:**
- Customer data processed via GenAI Hub stays within SAP's infrastructure (no data leaves to OpenAI/Google directly).
- SAP acts as a data processor; customer remains data controller.
- All AI processing is logged for audit purposes.
- Data is NOT used to train foundation models.
- GDPR-compliant data residency by region (EU10, US10, AP10).

---

### Q18. How does SAP AI Core differ from Azure ML or AWS SageMaker?

**A:**

| Aspect | SAP AI Core | Azure ML / SageMaker |
|--------|------------|---------------------|
| **Ecosystem** | Deep SAP integration | Cloud provider native |
| **Target users** | SAP customers extending S/4HANA | Any ML workload |
| **GenAI** | GenAI Hub built-in | Azure OpenAI / Bedrock |
| **Deployment** | BTP Cloud Foundry / Kyma | Azure AKS / SageMaker Endpoints |
| **Best for** | SAP-adjacent ML use cases | General-purpose ML |

---

### Q19. What is the `generative-ai-hub-sdk` package?

**A:** The official SAP Python SDK for interacting with GenAI Hub. It provides:
- `init_llm()` — Get a LangChain-compatible chat model.
- `init_embedding_model()` — Get a LangChain-compatible embedding model.
- `get_proxy_client()` — Get the authenticated proxy client.
- Authentication handling (reads from environment variables automatically).

```bash
pip install generative-ai-hub-sdk
# Also installs: langchain, langchain-openai, langchain-google-genai
```

---

### Q20. What environment variables does the GenAI Hub SDK need?

**A:**

```bash
# From your AI Core service key (download from BTP Cockpit)
AICORE_AUTH_URL=https://myorg.authentication.eu10.hana.ondemand.com
AICORE_CLIENT_ID=sb-your-client-id
AICORE_CLIENT_SECRET=your-client-secret
AICORE_BASE_URL=https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com
AICORE_RESOURCE_GROUP=default

# Set in .env file or Cloud Foundry environment
# The SDK reads these automatically — no manual token management needed!
```

---

> **💡 Viva Tip:** SAP Business AI and GenAI Hub will have questions like "How is this different from calling OpenAI directly?" The key answers are: **security** (data stays in SAP infrastructure), **compliance** (GDPR, audit), **integration** (native to BTP ecosystem), and **flexibility** (multi-model with one API).

---

*End of Unit 18 — SAP Business AI & GenAI Hub 🤖*
