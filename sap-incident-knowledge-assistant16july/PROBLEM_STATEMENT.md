# Hands-on Problem Statement

## Build a RAG Application Using Structured Excel Data

**Project Title:** SAP Incident Knowledge Assistant Using Structured Data and RAG

---

## 1. Business Scenario

An organization uses SAP systems such as SAP MM, SAP SD, SAP HANA, SAP BTP, and SAP SuccessFactors.

The IT support team maintains historical incident information in an Excel file. Each row represents one resolved incident and contains details such as:

- Incident ID
- SAP module
- Priority
- Category
- Issue description
- Root cause
- Resolution
- Support team
- Resolution time
- Incident status

Support engineers currently search the Excel file manually to find similar incidents and their resolutions. This process is slow, especially when:

- The Excel file contains thousands of incidents.
- The engineer does not know the exact incident ID.
- Similar incidents use different wording.
- Information is spread across several columns.
- New team members do not know previous solutions.

The organization wants to build a Retrieval-Augmented Generation application that allows users to ask questions in natural language and receive answers based only on the historical incident data.

---

## 2. Project Objective

Build a RAG application that:

- Reads structured incident data from an Excel file.
- Converts every Excel row into a meaningful text document.
- Preserves important structured fields as metadata.
- Generates embeddings for the incident records.
- Stores the embeddings in a vector database.
- Retrieves incidents that are semantically similar to a user question.
- Uses a large language model to generate a grounded answer.
- Displays the incident IDs and Excel row numbers used to generate the answer.

---

## 3. Suggested Technology Stack

- Python
- Google Colab
- Pandas
- LangChain
- Google Gemini
- Google Generative AI Embeddings
- ChromaDB or FAISS
- OpenPyXL
- Excel or CSV dataset

---

## 4. Sample Dataset Structure

Create an Excel file named `sap_incidents.xlsx`.

The Excel sheet should contain the following columns:

| Column | Description |
| --- | --- |
| incident_id | Unique incident identifier |
| incident_date | Date when the incident was reported |
| sap_module | SAP module affected |
| category | Type of issue |
| priority | Incident priority such as P1, P2, P3 or P4 |
| issue_summary | Short description of the issue |
| issue_description | Detailed explanation of the problem |
| root_cause | Identified cause of the incident |
| resolution | Steps used to resolve the issue |
| owner_team | Support team responsible |
| resolution_time_hours | Time required to resolve the incident |
| status | Current incident status |

---

## 5. Sample Data

| incident_id | sap_module | priority | category | issue_summary | root_cause | resolution | owner_team | resolution_time_hours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INC-1001 | SAP MM | P2 | Invoice Management | Supplier invoice blocked because of price variance | Incorrect purchase-order condition record | Corrected condition record and reprocessed invoice | Procure-to-Pay Support | 3.5 |
| INC-1002 | SAP HANA | P1 | Database Availability | HANA database became unavailable | Severe memory exhaustion | Released memory, restarted service and adjusted allocation limits | Database Platform Team | 5.0 |
| INC-1003 | SAP SD | P3 | Pricing | Incorrect discount in sales order | Incorrect pricing procedure sequence | Corrected condition sequence and repriced order | Order-to-Cash Support | 1.2 |
| INC-1004 | SAP BTP | P1 | Connectivity | Application could not connect to backend system | Expired destination credentials | Renewed credentials and corrected destination properties | BTP Platform Team | 7.5 |
| INC-1005 | SAP SuccessFactors | P2 | Integration | Employee replication was delayed | Mapping error in integration flow | Corrected mapping and reran integration job | HR Integration Team | 4.0 |
| INC-1006 | SAP HANA | P1 | Performance | Critical transactions became slow | Long-running savepoint and storage pressure | Corrected storage pressure and optimized workload | Database Platform Team | 9.0 |
| INC-1007 | SAP MM | P3 | Purchase Order | Purchase order release was not triggered | Incorrect release strategy configuration | Corrected release strategy and regenerated classification | Procure-to-Pay Support | 2.5 |
| INC-1008 | SAP BTP | P2 | Authorization | User could not access deployed application | Missing role collection assignment | Assigned required role collection | BTP Platform Team | 1.8 |

---

## 6. Core Hands-on Tasks

### Task 1: Load and Explore the Excel Data

Use Pandas to load the Excel file. Perform the following checks:

- Display the first five rows.
- Display column names.
- Check the number of records.
- Identify missing values.
- Check the data type of each column.
- Display the number of incidents by SAP module.
- Display the number of incidents by priority.

**Expected result:** The student should understand the structure and quality of the incident data before creating the RAG pipeline.

### Task 2: Clean and Prepare the Data

Perform suitable preprocessing:

- Remove completely empty rows.
- Replace missing text fields with suitable default values.
- Convert dates into a consistent format.
- Convert priority and SAP module names into consistent text.
- Convert resolution time into a numeric value.
- Remove unnecessary spaces and invalid characters.

**Expected result:** A clean dataframe ready for conversion into LangChain documents.

### Task 3: Convert Excel Rows into Documents

Convert every incident row into readable text.

Example:

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

Each row must become one LangChain Document.

Store the following values as metadata:

- source_type
- source_name
- sheet_name
- row_number
- incident_id
- sap_module
- priority
- category
- owner_team

**Expected result:** A list of LangChain documents where each document represents one incident.

### Task 4: Apply Row-Aware Chunking

Structured data should not be chunked in the same way as a long PDF. For this dataset:

- Keep one incident row as one logical document.
- Split the document only if an individual incident contains very long text.
- Preserve metadata after splitting.
- Assign a unique chunk ID, for example `INC-1006-chunk-1`.

**Expected result:** The meaning of each incident remains intact during retrieval.

### Task 5: Generate Embeddings

Use Google Generative AI embeddings to convert every incident document into a numerical vector.

Recommended embedding model: `gemini-embedding-001`

Perform a small test by embedding a sample question such as `HANA database performance issue`.

**Expected result:** The system should generate a vector representation of the question and incident records.

### Task 6: Create the Vector Database

Store the incident documents and their embeddings in ChromaDB or FAISS.

The vector database must store:

- Document text
- Embedding vector
- Incident metadata
- Source information

**Expected result:** All structured incident records are searchable using semantic similarity.

### Task 7: Test Semantic Retrieval

Test the vector database using questions such as:

- Which incident was related to HANA memory exhaustion?
- Find incidents involving SAP BTP connectivity problems.
- Which issue was caused by an incorrect pricing procedure?
- Show incidents related to employee integration failures.

For every retrieved result, display:

- Retrieval rank
- Incident ID
- SAP module
- Priority
- Excel row number
- Similarity score, when supported
- Retrieved document text

**Expected result:** The system should retrieve relevant incidents even when the user's wording is different from the wording in the Excel file.

### Task 8: Add Metadata Filtering

Allow the user to restrict retrieval using structured fields. Examples:

- Retrieve only P1 incidents.
- Search only SAP HANA incidents.
- Find SAP BTP incidents handled by the BTP Platform Team.

Apply metadata filters such as:

- `priority = P1`
- `sap_module = SAP HANA`
- `owner_team = BTP Platform Team`

**Expected result:** The application combines semantic search with structured filtering.

### Task 9: Create the RAG Prompt

Create a prompt instructing Gemini to:

- Answer only from the retrieved incident records.
- Never invent an incident or resolution.
- Mention the incident ID.
- Mention the SAP module and priority.
- Explain the resolution steps.
- Cite the Excel row number.
- State clearly when the answer is not available.

Suggested fallback response:

> I could not find sufficient information in the incident dataset to answer this question.

### Task 10: Build the Final RAG Function

Create a reusable function such as:

```python
ask_incident_rag(
    question,
    top_k=5,
    sap_module=None,
    priority=None
)
```

The function should:

- Accept the user's question.
- Apply optional metadata filters.
- Retrieve the most relevant incident records.
- Format the retrieved context.
- Send the question and context to Gemini.
- Return a grounded answer.
- Display the sources used.

---

## 7. Mandatory Test Questions

**Direct factual questions**

- What was the resolution for incident INC-1004?
- Which team resolved the employee replication issue?

**Semantic questions**

- Has there been an issue where a cloud application could not connect to an SAP backend?
- Find a previous incident involving database memory problems.

**Comparison questions**

- Which P1 incident took the longest time to resolve?
- Compare the two SAP HANA P1 incidents.

**Filter-based questions**

- Show only P1 SAP BTP incidents.
- Find SAP MM incidents handled by the Procure-to-Pay Support team.

**Recommendation-style questions**

- A user reports that a BTP application cannot access the backend because authentication is failing. Which previous incident is most similar, and what resolution should the support team investigate?

**Unsupported question**

- What is the annual revenue of the company?

The system should not invent an answer.

---

## 8. Expected Final Output

For the question:

> Which P1 SAP HANA incident took the longest to resolve?

The expected answer should be similar to:

> Incident INC-1006 took the longest to resolve among the retrieved P1 SAP HANA incidents.
> The incident was related to severe performance degradation caused by a long-running savepoint and storage pressure.
> The Database Platform Team corrected the storage pressure and optimized the workload.
> Resolution time: 9 hours.
> Source: sap_incidents.xlsx, Excel row 7.

---

## 9. Evaluation Criteria

| Area | Weight |
| --- | --- |
| Data loading and cleaning | 10% |
| Row-to-document conversion | 15% |
| Metadata preservation | 10% |
| Embedding and vector-store creation | 15% |
| Retrieval relevance | 20% |
| Grounded Gemini response | 15% |
| Source citation | 5% |
| Code structure and explanation | 10% |

---

## 10. Important Design Considerations

The student must explain:

- Why one Excel row is treated as one document.
- Why normal fixed-size chunking may damage structured records.
- Why metadata is important in structured-data RAG.
- How vector search differs from exact keyword search.
- Why structured filtering should be combined with semantic search.
- How hallucination is reduced using a grounded prompt.
- Why RAG may not be suitable for exact aggregation without additional logic.

---

## 11. Important Limitation to Address

Vector retrieval alone may not reliably answer questions involving calculations such as:

- What is the average resolution time for SAP HANA incidents?
- How many P1 incidents were reported?
- Which module has the highest average resolution time?

For such questions, the student should use:

- Pandas
- SQL
- A calculation tool
- An agent that routes analytical questions to structured-data processing

The recommended architecture is:

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

---

## 12. Bonus Tasks

Advanced learners may implement:

- Multiple Excel-sheet support
- Hybrid keyword and vector search
- Metadata-based filters
- Similarity score thresholds
- Query rewriting
- Retrieval reranking
- Conversation memory
- LangSmith or SAP BTP observability
- Streamlit user interface
- Deployment to SAP BTP Cloud Foundry
- SAP HANA Cloud Vector Engine instead of ChromaDB
- User feedback using thumbs-up and thumbs-down
- Evaluation dataset with expected answers
- Automatic groundedness checking

---

## 13. Final Deliverables

The student must submit:

- Google Colab notebook.
- Sample Excel dataset.
- Data-preparation explanation.
- RAG architecture diagram.
- Row-to-document conversion logic.
- Vector-store implementation.
- Final question-answering function.
- Results for all mandatory test questions.
- Screenshot of retrieved documents.
- Explanation of limitations and future improvements.

---

## 14. Final Learning Outcome

After completing this exercise, the learner should be able to:

- Build RAG using structured Excel data.
- Convert tabular records into meaningful documents.
- Preserve metadata for traceability.
- Perform semantic search over business records.
- Combine metadata filtering with vector retrieval.
- Generate grounded answers using Google Gemini.
- Identify when to use RAG and when to use SQL or Pandas.
- Design a structured-data RAG system suitable for enterprise use cases.
