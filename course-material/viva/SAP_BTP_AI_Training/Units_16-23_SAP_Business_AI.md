# 🏢 Units 16-23 — SAP Business AI (Complete Reference)

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 28–35 (64 hours)  
> **Dates**: 05-Aug-2026 to 14-Aug-2026  
> **Stream**: SAP BTP AI Training

> **Units covered in this file:**
> - Unit 16: SAP Overview (Day 28)
> - Unit 17: SAP CAPM & HANA Cloud (Day 29)
> - Unit 18: SAP Business AI & GenAI Hub (Day 30)
> - Unit 19: HANA Cloud Vector Engine + GenAI Hub (Day 31)
> - Unit 20: Orchestration & Document Grounding (Day 32)
> - Unit 21: Joule Skills with Joule Studio (Day 33)
> - Unit 22: Joule Walkthrough & SAP AI Agents (Day 34)
> - Unit 23: Assessment (Day 35)

---

# 📘 Unit 16 — SAP Overview

## 🔹 Section 1 — SAP Fundamentals

### Q1. What is SAP? What does it do?

**A:** **SAP (Systems, Applications & Products in Data Processing)** is a German multinational software corporation and the world's leading enterprise resource planning (ERP) software provider.

**What SAP does:**
- Provides software that runs **core business processes** for enterprises.
- Covers: Finance, HR, Supply Chain, Manufacturing, Sales, Procurement.
- Serves 99 of the 100 largest global companies.
- Used by 400,000+ businesses in 180+ countries.

**Key products:**
| Product | What It Manages |
|---------|----------------|
| **SAP S/4HANA** | ERP — Finance, Logistics, Manufacturing |
| **SAP SuccessFactors** | Human Capital Management |
| **SAP Ariba** | Procurement |
| **SAP Concur** | Travel & Expense |
| **SAP Analytics Cloud** | Business Intelligence |
| **SAP BTP** | Platform for extensions, integrations, AI |

---

### Q2. What is SAP ERP? How does it differ from SAP S/4HANA?

**A:**

| Aspect | SAP ECC (ERP Central Component) | SAP S/4HANA |
|--------|--------------------------------|-------------|
| **Database** | Any (Oracle, SQL Server, etc.) | SAP HANA only |
| **Architecture** | Traditional, complex | Simplified, modern |
| **Speed** | Standard | Much faster (in-memory HANA) |
| **UI** | SAP GUI (desktop) | SAP Fiori (web-based, responsive) |
| **Deployment** | On-premises | On-premises, cloud, or hybrid |
| **AI/ML** | Limited | Built-in AI with SAP AI Core |
| **End of mainstream maintenance** | 2027 | 2040+ |
| **Data model** | Rows and aggregates stored separately | Aggregates computed in real-time |

**S/4** = Suite for SAP HANA. **SAP's key message:** Migrate from ECC to S/4HANA before 2027.

---

### Q3. What is SAP BTP (Business Technology Platform)?

**A:** **SAP BTP** is SAP's **PaaS cloud platform** that provides tools and services for:

| Capability | Description |
|-----------|-------------|
| **Application Development** | Build custom apps and SAP extensions |
| **Integration** | Connect SAP and non-SAP systems |
| **Data & Analytics** | Store, process, and analyze data |
| **AI** | Train, deploy, and use AI models |

**BTP is the foundation for SAP's digital transformation strategy** — it's where you extend SAP without touching the core system ("clean core" principle).

---

### Q4. What is the SAP BTP subaccount and global account structure?

**A:**

```
Global Account (your organization's contract with SAP)
    ├── Subaccount A (Dev environment, EU10 region)
    │       ├── Cloud Foundry Space: Development
    │       └── Services: HANA Cloud, AI Core
    ├── Subaccount B (Staging environment, EU10 region)
    └── Subaccount C (Production environment, EU10 region)
```

| Concept | Description |
|---------|-------------|
| **Global Account** | Top-level contract; provides entitlements and quotas |
| **Subaccount** | Isolated environment; has its own services, users, and policies |
| **Directory** | Optional grouping of subaccounts |
| **Space** (CF) | Isolation within Cloud Foundry for deployments |
| **Namespace** (Kyma) | Isolation within Kubernetes |

---

### Q5. What are SAP BTP services?

**A:** SAP BTP provides 100+ services. Key ones:

| Category | Service | Purpose |
|----------|---------|---------|
| **Database** | SAP HANA Cloud | In-memory relational + vector database |
| **AI** | SAP AI Core | Train and deploy ML models |
| **AI** | SAP AI Launchpad | UI for managing AI workflows |
| **AI** | SAP GenAI Hub | Access to LLMs (GPT, Gemini, etc.) |
| **Integration** | SAP Integration Suite | Connect systems via APIs and event mesh |
| **Analytics** | SAP Analytics Cloud | Business intelligence and planning |
| **Development** | SAP Build Apps | Low-code application development |
| **Security** | XSUAA | Authorization and trust management |
| **Connectivity** | SAP Connectivity Service | Connect to on-premise systems |

---

## 🔹 Section 2 — SAP Fiori & UI

### Q6. What is SAP Fiori?

**A:** **SAP Fiori** is SAP's user experience (UX) design system and set of business applications with a modern, web-based, responsive UI.

**SAP Fiori Design Principles:**
1. **Role-based** — Each user sees what's relevant to their role.
2. **Responsive** — Works on desktop, tablet, mobile.
3. **Coherent** — Consistent look and feel across all SAP apps.
4. **Simple** — Focus on key tasks; remove complexity.
5. **Delightful** — Modern design, pleasant to use.

**Technology:** Built with **SAPUI5** (JavaScript UI framework) or **SAP Build Apps** (low-code).

---

# 📘 Unit 17 — SAP CAPM & HANA Cloud

## 🔹 Section 1 — SAP CAP (Cloud Application Programming Model)

### Q7. What is SAP CAP (Cloud Application Programming Model)?

**A:** **CAP** is SAP's opinionated framework for building cloud-native applications on SAP BTP. It provides:

- **CDS (Core Data Services)** — A domain modeling language to define data models and services.
- **Node.js / Java runtime** — Service implementations.
- **Built-in integrations** — HANA Cloud, SAP S/4HANA, XSUAA, OData/REST.

```
my-cap-project/
├── db/
│   └── schema.cds          ← Data model definition
├── srv/
│   ├── catalog-service.cds ← Service definition
│   └── catalog-service.js  ← Service implementation
└── package.json
```

**CDS data model example:**
```cds
// db/schema.cds
namespace my.company;

entity Employees {
  key ID        : UUID;
  name          : String(100);
  email         : String(100);
  department    : String(50);
  salary        : Decimal(10,2);
}
```

**CDS service definition:**
```cds
// srv/catalog-service.cds
using my.company.Employees from '../db/schema';

service CatalogService @(path: '/api') {
  entity Employees as projection on my.company.Employees;
}
// → CAP automatically generates OData/REST API for this!
```

---

### Q8. Why is CAP the recommended approach for SAP BTP applications?

**A:**

| Benefit | Description |
|---------|-------------|
| **Productivity** | Define data model once → CAP generates OData/REST API, UI annotations, database tables |
| **SAP best practices** | Built-in security (XSUAA), multitenancy, extensibility |
| **Database agnostic** | Works with SQLite (dev) → HANA Cloud (prod) |
| **Integrated** | Native connectors to S/4HANA, SuccessFactors, BTP services |
| **"Clean core"** | Extend SAP without modifying core — all extensions in BTP via CAP |

---

## 🔹 Section 2 — SAP HANA Cloud

### Q9. What is SAP HANA Cloud?

**A:** **SAP HANA Cloud** is a managed, in-memory cloud database on SAP BTP. It's the cloud-native version of SAP HANA.

**Key capabilities:**

| Capability | Description |
|-----------|-------------|
| **In-memory** | Data stored in RAM for ultra-fast queries |
| **Column-oriented** | Optimized for analytics (reads columns, not rows) |
| **Multi-model** | Relational + JSON + graph + spatial + vector in one database |
| **Built-in analytics** | Calculation views, PAL (Predictive Analysis Library) |
| **Vector Engine** | Store and search embeddings for RAG (Unit 19) |
| **Managed service** | SAP handles patching, backups, scaling |
| **Elastic storage** | Separate compute (in-memory) from disk storage |

---

### Q10. What is the difference between SAP HANA Cloud and a traditional database?

**A:**

| Aspect | Traditional DB (MySQL, PostgreSQL) | SAP HANA Cloud |
|--------|-----------------------------------|----------------|
| **Storage** | Disk (with cache) | In-memory (primary), disk for overflow |
| **Orientation** | Row | Column |
| **OLTP** | Excellent | Good |
| **OLAP** | Poor (needs data warehouse) | Excellent (both in one) |
| **Analytics** | Separate tools needed | Built-in calculation engine |
| **AI/ML** | External tools | Built-in PAL + Vector Engine |
| **Cost** | Low (open source) | High (enterprise) |
| **SAP integration** | None | Native integration with SAP ecosystem |

---

# 📘 Unit 18 — SAP Business AI & GenAI Hub

## 🔹 Section 1 — SAP Business AI

### Q11. What is SAP Business AI?

**A:** **SAP Business AI** is SAP's strategy to embed AI capabilities across all SAP products.

**Three pillars:**

| Pillar | Description | Examples |
|--------|-------------|---------|
| **Embedded AI** | AI built directly into SAP processes | Intelligent invoice matching, demand forecasting |
| **Business AI Platform** | Infrastructure for AI (SAP AI Core, AI Launchpad) | Build and deploy custom ML models |
| **Generative AI** | GenAI integrated into SAP products | SAP Joule, GenAI Hub |

**Key principles:**
- **Relevant** — AI for business processes, not generic chat.
- **Reliable** — AI grounded in business data, not hallucinations.
- **Responsible** — Ethics, transparency, GDPR compliance.

---

### Q12. What is SAP AI Core?

**A:** **SAP AI Core** is a managed service on SAP BTP for training and deploying ML models.

| Feature | Description |
|---------|-------------|
| **Training** | Run ML training jobs on Kubernetes-based infrastructure |
| **Serving** | Deploy models as REST APIs (inferencing endpoints) |
| **Orchestration** | Pipeline workflows for ML lifecycle |
| **Multi-tenancy** | Separate model access per tenant |
| **Foundation Models** | Access to SAP's and third-party foundation models |

**AI Core concepts:**
- **Scenario** — A collection of model versions and configurations.
- **Executable** — A Docker image with training/serving code.
- **Artifact** — Training data or model output stored in object storage.
- **Deployment** — A running model serving endpoint.

---

### Q13. What is SAP AI Launchpad?

**A:** **SAP AI Launchpad** is a web-based UI for managing the full ML lifecycle.

**What you can do:**
- View and manage AI Core resources (scenarios, executables, deployments).
- Monitor training jobs and deployments.
- View resource groups and configurations.
- Access and test deployed model endpoints.
- Manage GenAI Hub connections.

Think of it as the "dashboard" for SAP AI Core.

---

### Q14. What is SAP GenAI Hub?

**A:** **SAP GenAI Hub** is a service on SAP BTP that provides **unified, managed access to multiple foundation models** (LLMs) through a single API.

**Key benefits:**

| Benefit | Description |
|---------|-------------|
| **Multi-model access** | OpenAI GPT, Google Gemini, Meta LLaMA, Mistral — one API |
| **SAP security** | Data doesn't leave SAP's infrastructure; no training on your data |
| **Compliance** | GDPR, enterprise audit trails |
| **Harmonized API** | Same API format regardless of which model you use |
| **Cost management** | Track LLM usage and costs |
| **SAP integration** | Works natively with HANA Cloud, AI Core, CAP |

```python
# Using GenAI Hub via LangChain
from gen_ai_hub.proxy.langchain.init_models import init_llm, init_embedding_model

# Connect to GenAI Hub
llm = init_llm("gpt-4o", deployment_id="d2b32f...")
embeddings = init_embedding_model("text-embedding-ada-002", deployment_id="d3c45a...")

# Use exactly like any LangChain model!
response = llm.invoke("Explain SAP BTP in simple terms")
```

---

# 📘 Unit 19 — HANA Cloud Vector Engine + GenAI Hub

## 🔹 Section 1 — HANA Vector Engine

### Q15. What is the HANA Cloud Vector Engine?

**A:** **HANA Cloud Vector Engine** is a built-in capability of SAP HANA Cloud to store, index, and search **vector embeddings** — making HANA Cloud a native vector database for SAP RAG applications.

**Why it matters:**
- No need for a separate vector database (ChromaDB, Pinecone).
- Store embeddings alongside business data in the same HANA database.
- Combine vector search with SQL queries.
- Enterprise security and compliance.
- Native integration with GenAI Hub.

```sql
-- Create a table with a vector column in HANA Cloud
CREATE TABLE "DOCUMENT_CHUNKS" (
    "ID"        INTEGER PRIMARY KEY,
    "SOURCE"    NVARCHAR(200),
    "CHUNK_TEXT" NCLOB,
    "EMBEDDING" REAL_VECTOR(1536)   -- Store embedding vectors
);

-- Insert a chunk with its embedding
INSERT INTO "DOCUMENT_CHUNKS" VALUES (
    1,
    'hr_policy.txt',
    'Annual leave is 18 days per year.',
    TO_REAL_VECTOR('[0.023, -0.041, ...]')
);

-- Semantic search using cosine similarity
SELECT TOP 3 "CHUNK_TEXT", "SOURCE",
    COSINE_SIMILARITY("EMBEDDING", TO_REAL_VECTOR('[0.025, -0.038, ...]')) AS SIMILARITY
FROM "DOCUMENT_CHUNKS"
ORDER BY SIMILARITY DESC;
```

---

### Q16. How do you build a SAP-native RAG pipeline with HANA Vector + GenAI Hub?

**A:**

```python
from hdbcli import dbapi
from gen_ai_hub.proxy.langchain import init_llm, init_embedding_model
from langchain_community.vectorstores import HanaDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Connect to HANA Cloud
conn = dbapi.connect(
    address="your-hana.hanacloud.ondemand.com",
    port=443,
    user="DBADMIN",
    password="...",
    encrypt=True
)

# 2. Initialize models from GenAI Hub
embeddings = init_embedding_model("text-embedding-ada-002", deployment_id="...")
llm = init_llm("gpt-4o", deployment_id="...")

# 3. Set up HANA as vector store
vector_store = HanaDB(
    connection=conn,
    embedding=embeddings,
    table_name="HR_POLICY_CHUNKS"
)

# 4. Ingest documents
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(document_text)
vector_store.add_texts(chunks, metadatas=[{"source": "hr_policy.txt"}] * len(chunks))

# 5. RAG Query
retriever = vector_store.as_retriever(search_kwargs={"k": 3})
relevant_docs = retriever.invoke("How many annual leaves?")

context = "\n\n".join([d.page_content for d in relevant_docs])
prompt = f"Answer using only this context:\n{context}\n\nQ: How many annual leaves?"
answer = llm.invoke(prompt).content
```

---

# 📘 Unit 20 — Orchestration & Document Grounding

### Q17. What is SAP AI Core Orchestration?

**A:** **SAP AI Core Orchestration** is a high-level service that manages complex GenAI workflows — routing requests through multiple steps: model access, grounding, filtering, and response generation.

**Orchestration pipeline components:**

| Component | Role |
|-----------|------|
| **LLM selection** | Choose which foundation model to use |
| **Templating** | Apply prompt templates with business data |
| **Grounding** | Inject relevant documents (like RAG) |
| **Input filtering** | Detect and block harmful inputs |
| **Output filtering** | Filter harmful or inappropriate outputs |
| **Response** | Return grounded, safe, structured answer |

---

### Q18. What is Document Grounding in SAP?

**A:** **Document Grounding** in SAP context means connecting the AI to specific **SAP documents and business data** to generate accurate, grounded answers — essentially SAP's managed RAG.

**Sources for grounding:**
- SharePoint documents
- SAP Help documentation
- Custom knowledge bases (uploaded documents)
- HANA Cloud Vector Engine

```python
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

client = AICoreV2Client(base_url="...", auth_url="...", client_id="...", client_secret="...")

# Grounding configuration
grounding_config = {
    "grounding": {
        "type": "document_grounding",
        "config": {
            "input_params": ["grounding_request"],
            "output_param": "grounding_output",
            "groundings": [{
                "type": "hana",
                "config": {
                    "table": "HR_POLICY_CHUNKS",
                    "search_config": {"limit": 5}
                }
            }]
        }
    }
}
```

---

# 📘 Unit 21 — Joule Skills with Joule Studio

### Q19. What is SAP Joule?

**A:** **SAP Joule** is SAP's AI copilot — embedded across SAP products to help business users work more efficiently through natural language.

**Key capabilities:**
- **Natural language queries** — Ask questions, get business insights without knowing report names.
- **Process automation** — "Create a purchase order for 100 units of X."
- **Guided actions** — Step-by-step help for complex SAP transactions.
- **Cross-system** — Works across S/4HANA, SuccessFactors, Ariba, BTP.
- **Grounded** — Answers based on your actual SAP data, not general knowledge.

**Example interactions:**
```
User: "Show me all overdue invoices for vendor SAP AG"
Joule: [Queries SAP system] → Shows filtered invoice list

User: "Create leave request for 3 days from August 25"
Joule: [Pre-fills form in SuccessFactors] → "Please review and submit"

User: "What's the status of my expense report #EXP-2026-1234?"
Joule: [Queries SAP Concur] → "Your report is approved. Payment scheduled for..."
```

---

### Q20. What is Joule Studio?

**A:** **Joule Studio** is a development environment on SAP BTP for building and customizing **Joule Skills** — custom AI capabilities that extend what Joule can do for your organization.

**Joule Skill = Custom capability added to Joule:**
- Define what topics/intents the skill handles.
- Configure data sources (which SAP tables/APIs to query).
- Design the response template.
- Test and publish to make available to users.

**Types of Joule Skills:**
- **Information retrieval** — Query business data and return results.
- **Process automation** — Trigger SAP transactions from natural language.
- **Document Q&A** — Answer questions from custom document knowledge bases.

---

# 📘 Unit 22 — Joule Walkthrough & SAP AI Agents

### Q21. What is an SAP AI Agent? How does it differ from Joule?

**A:**

| Aspect | SAP Joule | SAP AI Agent |
|--------|----------|--------------|
| **Interaction** | Conversational, guided | Autonomous task execution |
| **Human control** | Always asks before acting | Can act autonomously (within policies) |
| **Complexity** | Single-step or guided multi-step | Multi-step autonomous workflow |
| **Customization** | Joule Skills | Full agent with tools and planning |
| **Best for** | Business user assistance | Automated end-to-end processes |

**SAP AI Agent example:**
```
Goal: "Process all pending invoices from this week"

Agent autonomously:
1. Queries S/4HANA for pending invoices
2. Validates each invoice against PO
3. Routes approved invoices for payment
4. Flags exceptions for human review
5. Generates processing report
→ All without human intervention (except flagged exceptions)
```

---

### Q22. What tools and integrations are available to SAP AI Agents?

**A:**

| Tool/Integration | What It Enables |
|-----------------|----------------|
| **SAP S/4HANA APIs** | Read/write ERP data (orders, invoices, inventory) |
| **SAP SuccessFactors** | HR actions (leave approval, payroll queries) |
| **SAP Ariba** | Procurement actions |
| **HANA Cloud** | Query business data |
| **SAP Integration Suite** | Connect to external systems |
| **Document grounding** | Answer from documents |
| **GenAI Hub** | LLM generation |
| **External APIs** | Any REST API (via HTTP tool) |

---

# 📘 Unit 23 — Assessment

## 🔹 Complete SAP BTP AI Review

### Q23. Explain the complete SAP AI architecture from data to answer.

**A:**

```
Business Data Sources
    ├── SAP S/4HANA (business transactions)
    ├── SAP SuccessFactors (HR data)
    └── Documents (HR policies, manuals)
                ↓
         [SAP HANA Cloud]
    ├── Relational tables (business data)
    └── Vector Engine (document embeddings)
                ↓
         [SAP GenAI Hub]
    ├── Embedding model (text → vectors)
    └── LLM (vector context → grounded answer)
                ↓
         [SAP AI Core Orchestration]
    ├── Grounding module (RAG retrieval)
    ├── Input/Output filtering
    └── Response generation
                ↓
         [SAP Joule / Custom App]
    └── User receives grounded, safe, business answer
```

---

### Q24. What is RISE with SAP?

**A:** **RISE with SAP** is SAP's bundled cloud transformation package — a subscription that includes:
- **SAP S/4HANA Cloud** — The ERP.
- **SAP BTP** — The platform for extensions and AI.
- **Business Process Intelligence** — Process mining tools.
- **SAP Business Network** — Supplier and trading partner connectivity.
- **SAP Partner Ecosystem** — Preferred implementation partners.

**In simple terms:** RISE with SAP is the "complete package" for enterprises migrating from on-premises SAP to the cloud. One contract, one provider, end-to-end transformation.

---

### Q25. What are the SAP BTP environments and when do you use each?

**A:**

| Environment | When to Use | Runtime | Best For |
|-------------|------------|---------|----------|
| **Cloud Foundry** | Traditional web apps, microservices | Language buildpacks | Node.js/Python/Java apps, quick prototypes |
| **Kyma** | Containerized, event-driven, complex | Kubernetes | Docker containers, event-based processing |
| **ABAP** | Extend classic SAP ABAP-based systems | ABAP runtime | Classic SAP extensions using ABAP language |
| **SAP Build** | Low-code/no-code | Managed | Business apps without coding |

---

### Q26. What is OData? Why is it important in SAP?

**A:** **OData (Open Data Protocol)** is a REST-based protocol for exposing and consuming data via APIs. SAP uses OData as the primary API standard for:

- **SAP Fiori apps** consume backend data via OData services.
- **SAP CAP** auto-generates OData and REST APIs from CDS models.
- **S/4HANA APIs** are exposed as OData services.

**OData features:**
- CRUD operations via HTTP.
- Query parameters: `$filter`, `$select`, `$top`, `$expand`, `$orderby`.
- Metadata via `$metadata` endpoint.

```
GET /odata/v4/catalog/Employees?$filter=salary gt 70000&$select=name,salary&$top=10
```

---

### Q27. What is the SAP Integration Suite?

**A:** **SAP Integration Suite** is SAP's middleware platform for connecting SAP and non-SAP systems.

| Capability | Description |
|-----------|-------------|
| **Cloud Integration** | Build integration flows (iFlows) to exchange data |
| **API Management** | Publish, manage, and secure APIs |
| **Event Mesh** | Asynchronous event-based communication |
| **Integration Advisor** | AI-assisted EDI/B2B message mapping |
| **Open Connectors** | 170+ pre-built connectors to non-SAP systems |

**Example use case:** Sales order created in S/4HANA → Integration Suite → Sent to Salesforce CRM → Confirmation back to S/4HANA.

---

### Q28. How does SAP handle AI governance and compliance?

**A:** SAP follows its **"Responsible AI" framework:**

| Principle | SAP Implementation |
|-----------|-------------------|
| **Transparency** | Model cards for all SAP AI models; audit trails |
| **Data privacy** | GDPR-compliant; customer data never used for training |
| **Fairness** | Bias testing in SAP models |
| **Security** | Data processed within SAP's infrastructure |
| **Human oversight** | Joule always shows sources; human approval for actions |
| **Compliance** | SOC 2, ISO 27001, GDPR, industry-specific certifications |

---

### Q29. What is SAP Build?

**A:** **SAP Build** is SAP's low-code/no-code development platform:

| Tool | What It Does |
|------|-------------|
| **SAP Build Apps** | Visual app development (drag and drop) |
| **SAP Build Process Automation** | Workflow and RPA automation |
| **SAP Build Work Zone** | Unified employee portal |
| **SAP Build Code** | AI-assisted coding (with Joule for code) |

**Target users:** Business users and citizen developers who can't code but need to build applications.

---

### Q30. How would you architect a complete GenAI document Q&A solution on SAP BTP?

**A:**

```
ARCHITECTURE:

[Documents] → SAP BTP Storage
                    ↓
             CAP Service (document ingestion endpoint)
                    ↓
             Text splitting + Embedding (via GenAI Hub)
                    ↓
             SAP HANA Cloud Vector Engine (store embeddings)
                    ↓
             CAP Service (/ask endpoint)
                    ↓
             Query embedding → Vector similarity search (HANA) → Top-K chunks
                    ↓
             SAP AI Core Orchestration (grounding + LLM call)
                    ↓
             SAP Fiori UI (built with SAPUI5)
                    ↓
             SAP Joule integration (available in Joule sidebar)

SERVICES USED:
  - SAP BTP (Cloud Foundry runtime)
  - SAP HANA Cloud (relational + vector)
  - SAP AI Core (orchestration)
  - SAP GenAI Hub (embedding + LLM)
  - SAP Build Apps (optional UI)
  - SAP Joule (optional copilot integration)
```

---

> **💡 Viva Tips for SAP Modules:**
> 1. **Know the ecosystem** — BTP, HANA Cloud, GenAI Hub, AI Core, Joule all fit together. Be able to explain HOW.
> 2. **Connect to your project** — "Our hackathon project used a custom RAG; in SAP, this would be done with HANA Vector + GenAI Hub Orchestration."
> 3. **RISE with SAP** — Know what it means for enterprises migrating to cloud.
> 4. **SAP vs generic tools** — Always highlight what makes SAP's approach enterprise-grade (compliance, integration, clean core).

---

*End of Units 16-23 — SAP Business AI 🏢*
