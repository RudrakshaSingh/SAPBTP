# Problem Statement 12 — SAP Incident Knowledge Assistant (RAG over Structured Excel Data)

| | |
|---|---|
| **Project Title** | SAP Incident Knowledge Assistant Using Structured Data and RAG |
| **Domain** | Enterprise IT Support / SAP Operations |
| **Topic** | RAG over structured (tabular) data, row-aware chunking, metadata filtering |
| **Stack** | Python · Pandas · OpenPyXL · LangChain · Google Gemini · Gemini Embeddings · ChromaDB or FAISS |
| **Implementation** | [`12-sap-incident-knowledge-assistant16july/`](../12-sap-incident-knowledge-assistant16july/) |

---

## 1. Business Scenario

An organization uses SAP systems such as SAP MM, SAP SD, SAP HANA, SAP BTP, and SAP SuccessFactors.

The IT support team maintains historical incident information in an Excel file. Each row represents one resolved incident and contains the incident ID, SAP module, priority, category, issue description, root cause, resolution, support team, resolution time, and status.

Support engineers currently search the Excel file manually to find similar incidents and their resolutions. This is slow, especially when:

- The Excel file contains thousands of incidents.
- The engineer does not know the exact incident ID.
- Similar incidents use different wording.
- Information is spread across several columns.
- New team members do not know previous solutions.

The organization wants a **Retrieval-Augmented Generation** application that lets users ask questions in natural language and receive answers grounded **only** in the historical incident data.

## 2. Project Objective

Build a RAG application that:

- Reads structured incident data from an Excel file.
- Converts every Excel row into a meaningful text document.
- Preserves important structured fields as metadata.
- Generates embeddings for the incident records.
- Stores the embeddings in a vector database.
- Retrieves incidents semantically similar to a user question.
- Uses an LLM to generate a grounded answer.
- Displays the incident IDs and **Excel row numbers** used to generate the answer.

---

## 3. Dataset Structure

Create an Excel file named `sap_incidents.xlsx` with these columns:

| Column | Description |
|---|---|
| `incident_id` | Unique incident identifier |
| `incident_date` | Date when the incident was reported |
| `sap_module` | SAP module affected |
| `category` | Type of issue |
| `priority` | P1, P2, P3 or P4 |
| `issue_summary` | Short description of the issue |
| `issue_description` | Detailed explanation of the problem |
| `root_cause` | Identified cause of the incident |
| `resolution` | Steps used to resolve the issue |
| `owner_team` | Support team responsible |
| `resolution_time_hours` | Time required to resolve the incident |
| `status` | Current incident status |

### Sample Data

| incident_id | sap_module | priority | category | issue_summary | root_cause | resolution | owner_team | resolution_time_hours |
|---|---|---|---|---|---|---|---|---|
| INC-1001 | SAP MM | P2 | Invoice Management | Supplier invoice blocked because of price variance | Incorrect purchase-order condition record | Corrected condition record and reprocessed invoice | Procure-to-Pay Support | 3.5 |
| INC-1002 | SAP HANA | P1 | Database Availability | HANA database became unavailable | Severe memory exhaustion | Released memory, restarted service and adjusted allocation limits | Database Platform Team | 5.0 |
| INC-1003 | SAP SD | P3 | Pricing | Incorrect discount in sales order | Incorrect pricing procedure sequence | Corrected condition sequence and repriced order | Order-to-Cash Support | 1.2 |
| INC-1004 | SAP BTP | P1 | Connectivity | Application could not connect to backend system | Expired destination credentials | Renewed credentials and corrected destination properties | BTP Platform Team | 7.5 |
| INC-1005 | SAP SuccessFactors | P2 | Integration | Employee replication was delayed | Mapping error in integration flow | Corrected mapping and reran integration job | HR Integration Team | 4.0 |
| INC-1006 | SAP HANA | P1 | Performance | Critical transactions became slow | Long-running savepoint and storage pressure | Corrected storage pressure and optimized workload | Database Platform Team | 9.0 |
| INC-1007 | SAP MM | P3 | Purchase Order | Purchase order release was not triggered | Incorrect release strategy configuration | Corrected release strategy and regenerated classification | Procure-to-Pay Support | 2.5 |
| INC-1008 | SAP BTP | P2 | Authorization | User could not access deployed application | Missing role collection assignment | Assigned required role collection | BTP Platform Team | 1.8 |

---

## 4. Core Hands-on Tasks

### Task 1: Load and Explore the Excel Data

Use Pandas to load the file and check: first five rows, column names, record count, missing values, data type of each column, incident count by SAP module, incident count by priority.

**Expected result:** understand the structure and quality of the incident data before building the pipeline.

### Task 2: Clean and Prepare the Data

- Remove completely empty rows.
- Replace missing text fields with suitable defaults.
- Convert dates into a consistent format.
- Normalize priority and SAP module names.
- Convert resolution time into a numeric value.
- Remove unnecessary spaces and invalid characters.

**Expected result:** a clean dataframe ready for conversion into LangChain documents.

### Task 3: Convert Excel Rows into Documents

Convert every incident row into readable text:

```text
Incident ID: INC-1006
SAP Module: SAP HANA
Priority: P1
Category: Performance
Issue Summary: Critical transactions became slow
Issue Description: Users experienced severe performance degradation.
Root Cause: Long-running savepoint and storage pressure
Resolution: Corrected storage pressure and optimized workload
Owner Team: Database Platform Team
Resolution Time: 9 hours
Status: Closed
```

Each row becomes **one** LangChain `Document`. Store as metadata: `source_type`, `source_name`, `sheet_name`, `row_number`, `incident_id`, `sap_module`, `priority`, `category`, `owner_team`.

### Task 4: Apply Row-Aware Chunking

Structured data must not be chunked like a long PDF:

- Keep one incident row as one logical document.
- Split only if an individual incident contains very long text.
- Preserve metadata after splitting.
- Assign a unique chunk ID, e.g. `INC-1006-chunk-1`.

**Expected result:** the meaning of each incident stays intact during retrieval.

### Task 5: Generate Embeddings

Use Google Generative AI embeddings (recommended: `gemini-embedding-001`). Test by embedding a sample question such as `HANA database performance issue`.

### Task 6: Create the Vector Database

Store documents and embeddings in ChromaDB or FAISS. The store must hold: document text, embedding vector, incident metadata, source information.

### Task 7: Test Semantic Retrieval

Test with questions such as:

- Which incident was related to HANA memory exhaustion?
- Find incidents involving SAP BTP connectivity problems.
- Which issue was caused by an incorrect pricing procedure?
- Show incidents related to employee integration failures.

For every retrieved result display: retrieval rank, incident ID, SAP module, priority, Excel row number, similarity score (when supported), retrieved document text.

**Expected result:** relevant incidents are retrieved even when the user's wording differs from the Excel text.

### Task 8: Add Metadata Filtering

Allow retrieval to be restricted using structured fields — `priority = P1`, `sap_module = SAP HANA`, `owner_team = BTP Platform Team`.

**Expected result:** the application combines semantic search with structured filtering.

### Task 9: Create the RAG Prompt

Instruct Gemini to:

- Answer only from the retrieved incident records.
- Never invent an incident or resolution.
- Mention the incident ID, SAP module, and priority.
- Explain the resolution steps.
- Cite the Excel row number.
- State clearly when the answer is not available.

Suggested fallback:

> I could not find sufficient information in the incident dataset to answer this question.

### Task 10: Build the Final RAG Function

```python
ask_incident_rag(
    question,
    top_k=5,
    sap_module=None,
    priority=None
)
```

It should accept the question, apply optional metadata filters, retrieve the most relevant records, format the context, send question + context to Gemini, return a grounded answer, and display the sources used.

---

## 5. Mandatory Test Questions

| Type | Questions |
|---|---|
| **Direct factual** | What was the resolution for incident INC-1004? · Which team resolved the employee replication issue? |
| **Semantic** | Has there been an issue where a cloud application could not connect to an SAP backend? · Find a previous incident involving database memory problems. |
| **Comparison** | Which P1 incident took the longest time to resolve? · Compare the two SAP HANA P1 incidents. |
| **Filter-based** | Show only P1 SAP BTP incidents. · Find SAP MM incidents handled by the Procure-to-Pay Support team. |
| **Recommendation-style** | A user reports that a BTP application cannot access the backend because authentication is failing. Which previous incident is most similar, and what resolution should the support team investigate? |
| **Unsupported** | What is the annual revenue of the company? |

The system must **not** invent an answer to the unsupported question.

---

## 6. Expected Final Output

For the question:

> Which P1 SAP HANA incident took the longest to resolve?

The answer should be similar to:

> Incident INC-1006 took the longest to resolve among the retrieved P1 SAP HANA incidents.
> The incident was related to severe performance degradation caused by a long-running savepoint and storage pressure.
> The Database Platform Team corrected the storage pressure and optimized the workload.
> Resolution time: 9 hours.
> Source: sap_incidents.xlsx, Excel row 7.

---

## 7. Evaluation Criteria

| Area | Weight |
|---|---|
| Data loading and cleaning | 10% |
| Row-to-document conversion | 15% |
| Metadata preservation | 10% |
| Embedding and vector-store creation | 15% |
| Retrieval relevance | 20% |
| Grounded Gemini response | 15% |
| Source citation | 5% |
| Code structure and explanation | 10% |

## 8. Design Considerations to Explain

- Why one Excel row is treated as one document.
- Why normal fixed-size chunking may damage structured records.
- Why metadata is important in structured-data RAG.
- How vector search differs from exact keyword search.
- Why structured filtering should be combined with semantic search.
- How hallucination is reduced using a grounded prompt.
- Why RAG may not be suitable for exact aggregation without additional logic.

## 9. Important Limitation to Address

Vector retrieval alone cannot reliably answer calculation questions such as:

- What is the average resolution time for SAP HANA incidents?
- How many P1 incidents were reported?
- Which module has the highest average resolution time?

For these, use Pandas, SQL, a calculation tool, or an agent that routes analytical questions to structured-data processing. Recommended architecture:

```text
User Question
      ↓
Question Classification
      ↓
┌───────────────────────┬────────────────────────┐
│ Semantic question     │ Analytical question    │
│                       │                        │
│ Vector RAG            │ Pandas or SQL          │
└───────────────────────┴────────────────────────┘
      ↓
Combined grounded response
```

## 10. Bonus Tasks

Multiple Excel-sheet support · hybrid keyword + vector search · metadata-based filters · similarity score thresholds · query rewriting · retrieval reranking · conversation memory · LangSmith or SAP BTP observability · Streamlit UI · deployment to SAP BTP Cloud Foundry · SAP HANA Cloud Vector Engine instead of ChromaDB · thumbs-up/thumbs-down feedback · evaluation dataset with expected answers · automatic groundedness checking.

## 11. Final Deliverables

1. Google Colab notebook
2. Sample Excel dataset
3. Data-preparation explanation
4. RAG architecture diagram
5. Row-to-document conversion logic
6. Vector-store implementation
7. Final question-answering function
8. Results for all mandatory test questions
9. Screenshot of retrieved documents
10. Explanation of limitations and future improvements

## 12. Final Learning Outcome

After completing this exercise, the learner will be able to build RAG over structured Excel data, convert tabular records into meaningful documents, preserve metadata for traceability, perform semantic search over business records, combine metadata filtering with vector retrieval, generate grounded answers using Gemini, identify when to use RAG versus SQL/Pandas, and design a structured-data RAG system suitable for enterprise use.
