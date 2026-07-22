# SAP Incident Knowledge Assistant

A Retrieval-Augmented Generation application over **structured Excel data**. Support engineers ask questions in plain English and get answers grounded strictly in the historical incident sheet, with the incident ID and Excel row number cited for every claim.

Full brief: [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md)

---

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

cp .env.example .env            # then paste your key from https://aistudio.google.com/apikey

python create_dataset.py        # writes sap_incidents.xlsx
python run_demo.py              # runs every task and every mandatory test question
```

Use it from your own code:

```python
from incident_rag import build_assistant, ask_incident_rag, answer_question

store, df = build_assistant()

# Task 10 -- semantic RAG with optional metadata filters
ask_incident_rag("Why could the app not reach the backend?", store,
                 top_k=5, sap_module="SAP BTP", priority="P1").display()

# Task 11 -- routes calculations to Pandas, everything else to RAG
answer_question("What is the average resolution time for SAP HANA incidents?", store, df).display()
```

## Files

| File | Purpose |
| --- | --- |
| [SAP_Incident_Knowledge_Assistant_Colab.ipynb](SAP_Incident_Knowledge_Assistant_Colab.ipynb) | The Colab notebook — the whole pipeline, task by task |
| [create_dataset.py](create_dataset.py) | Builds `sap_incidents.xlsx` (20 incidents + deliberately messy rows) |
| [incident_rag.py](incident_rag.py) | The pipeline: Tasks 1-11 |
| [run_demo.py](run_demo.py) | Runs Tasks 7-8 and every mandatory test question |
| [generate_notebook.py](generate_notebook.py) | Rebuilds the notebook from the modules |
| [demo_output.txt](demo_output.txt) | Captured output of a full run |
| [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md) | The original brief |

### Notebook or modules?

Both run the same code. The notebook is the teaching artefact — upload it to Colab,
add a `GOOGLE_API_KEY` secret, and run top to bottom; it installs its own
dependencies and writes its own dataset, so it needs nothing else from this folder.
The modules are the reusable version.

They cannot drift apart: `generate_notebook.py` builds the notebook *from*
`incident_rag.py` and `create_dataset.py`, so edit the modules and regenerate —
don't edit the notebook's code cells by hand.

## Architecture

```text
sap_incidents.xlsx  (one incident per row)
        │
        │  Task 1-2   Pandas: load, stamp Excel row number, explore, clean
        ▼
  Clean dataframe ──────────────────────────────┐
        │                                        │
        │  Task 3     one row -> one Document    │
        │             (labelled text + metadata) │
        ▼                                        │
  LangChain Documents                            │
        │                                        │
        │  Task 4     row-aware chunking         │
        ▼             (split only if oversized)  │
     Chunks                                      │
        │                                        │
        │  Task 5     Gemini gemini-embedding-001│
        ▼                                        │
    Embeddings                                   │
        │                                        │
        │  Task 6                                │
        ▼                                        │
   FAISS vector store                            │
        │                                        │
        └───────────────┬────────────────────────┘
                        │
                  User question
                        │
                        ▼
              Question classification          (Task 11)
                        │
        ┌───────────────┴────────────────┐
        │                                │
  Semantic question               Analytical question
        │                                │
  Tasks 7-8                       Pandas aggregates
  vector search                   over ALL rows
  + metadata filter                      │
        │                                │
        ▼                                ▼
  Retrieved records                 Exact statistics
        │                                │
        └───────────────┬────────────────┘
                        │
                  Task 9 grounded prompt
                        ▼
                  Google Gemini
                        │
                        ▼
        Answer + incident IDs + Excel row citations
```

---

## Design considerations

### Why one Excel row is treated as one document

A row *is* the unit of meaning here. Everything an engineer needs — the symptom, the root cause, the fix, the team, the time — lives on one line, and those fields only make sense together. "Expired destination credentials" is useless without the symptom it explains. Retrieving one row therefore retrieves one complete, self-contained answer, and it maps cleanly onto one citation: `sap_incidents.xlsx`, Excel row 5.

### Why normal fixed-size chunking may damage structured records

Splitting every 500 or 1,000 characters ignores row boundaries. A 500-character window over this sheet would cut between `Root Cause:` and `Resolution:`, or merge the tail of INC-1004 with the head of INC-1005. Two specific failures follow:

- **Severed fields.** A chunk holding a root cause but not its resolution retrieves well and answers nothing.
- **Blended records.** A chunk spanning two incidents lets the model attribute INC-1005's fix to INC-1004 — a hallucination the retrieval step handed it.

So `chunk_documents` splits only when a single record exceeds ~1,500 characters. In this dataset the longest record is 587 characters, so all 20 rows stay intact — the splitter is insurance for one unusually verbose incident, not the normal path.

### Why metadata is important in structured-data RAG

Embedding a row flattens it into a single vector; the columns stop being addressable. Metadata keeps them:

- **Traceability.** `row_number` and `incident_id` survive the whole pipeline, so every sentence can be traced back to a line a human can open in Excel.
- **Filtering.** `priority` and `sap_module` as metadata make "only P1" a guarantee rather than a hint (below).
- **Provenance.** `source_name` and `sheet_name` mean the answer stays attributable when a second workbook is added.

### How vector search differs from exact keyword search

Keyword search matches characters; vector search matches meaning. The query *"Has there been an issue where a cloud application could not connect to an SAP backend?"* shares almost no distinctive keywords with INC-1004's text ("Cloud Foundry application ... failed every call to the on-premise backend"), yet it ranks first, because the embedding places the two near each other in vector space. `LIKE '%cloud application%'` returns nothing. That is the whole reason RAG beats the manual Ctrl+F workflow this project replaces.

The flip side: vector search has no notion of *exactly*. It returns the k nearest rows, never "all rows matching X" and never a count. Hence the next two sections.

### Why structured filtering should be combined with semantic search

Similarity is a soft signal, so "Show only P1 SAP BTP incidents" is not enforceable by embeddings — a P2 incident that *reads* like a crisis can out-rank a terse P1. Priority, however, is a fact recorded in a column. Filtering on metadata makes it a hard constraint and lets similarity do only what it is good at: ranking the survivors by relevance.

```python
retrieve(store, "connection failures", sap_module="SAP BTP", priority="P1")
# semantic ranking, but a non-P1 BTP row is now structurally unreachable
```

This is also why `clean_incidents` normalises `"  sap hana  "` to `SAP HANA` before indexing. An un-normalised value doesn't just look untidy — it makes the row invisible to `sap_module="SAP HANA"` forever.

### How hallucination is reduced using a grounded prompt

Four mechanisms stack:

1. **Closed-book instruction.** The prompt tells Gemini to use only the retrieved records and never invent an incident, cause, team or number.
2. **A mandatory fallback.** When the context doesn't cover the question, the model must reply with one fixed sentence. Refusal is an explicit, easy path rather than a failure state the model has to improvise around.
3. **Forced citation.** Every claim must carry an incident ID and Excel row. A fabricated fact has no row number to cite, which makes inventing one visibly harder — and any slip auditable by the reader.
4. **`temperature=0`.** No sampling creativity in what is fundamentally a lookup task.

Verified: *"What is the annual revenue of the company?"* returns the fallback rather than a guess.

### Why RAG may not be suitable for exact aggregation without additional logic

*"How many P1 incidents were reported?"* is unanswerable by retrieval, by construction. Top-k returns 5 rows; the answer is 6. The model would faithfully count what it was given and confidently report **5** — grounded in its context and still wrong. Averages fail the same way, and worse: an average over the 5 most *similar* rows is not an average over the dataset, it's an average over a biased sample nobody asked for.

The fix isn't a better prompt, it's a different engine. See below.

---

## Limitation: aggregation, and how this project addresses it

`answer_question` classifies the question first (Task 11):

- **Analytical** ("how many", "average", "which module has the highest") → `compute_statistics` runs Pandas over the **whole** dataframe and Gemini phrases the exact numbers.
- **Semantic** (everything else) → vector RAG with citations.

Either branch keeps the same grounded prompt and the same fallback sentence, so the refusal behaviour holds on both paths.

| Question | Route | Answer |
| --- | --- | --- |
| How many P1 incidents were reported? | Pandas | 6 |
| Average resolution time for SAP HANA? | Pandas | 5.10 hours |
| Which module has the highest average resolution time? | Pandas | SAP HANA, 5.10 hours |
| Which P1 incident took the longest? | Pandas | INC-1006, 9 hours |
| Compare the two SAP HANA P1 incidents | Vector RAG | INC-1002 vs INC-1006, cited |

The Pandas branch works here because the dataset is small enough to summarise fully into the prompt. At thousands of incidents that digest stops fitting in the context window, and the aggregate step should become a real tool call — a `pandas.query` tool or SQL over the sheet — with the LLM writing the query rather than reading a pre-computed digest.

## Other known limitations

- **Retrieval is unfiltered by score.** Every query returns `top_k` rows even when nothing is relevant; the grounded prompt catches this at the answer stage, but a distance threshold would stop weak context from being sent at all.
- **The classifier is one LLM call with no fallback.** A misrouted question degrades quietly — a count sent to the semantic branch answers from 5 rows without saying so.
- **FAISS filters post-search.** `fetch_k` is set to `max(50, top_k*10)`; on a much larger sheet a narrow filter could exhaust the candidate pool before finding matches. Chroma's native `where` clause or a metadata-first pre-filter would scale better.
- **Filters are exact-match only** — no ranges (`resolution_time_hours > 5`) and no OR conditions.
- **No conversation memory.** Each question is independent; follow-ups like "and who fixed that one?" won't resolve.
- **The index is rebuilt on every run.** Fine for 20 rows, wasteful at scale — `FAISS.save_local` / `load_local` would persist it.

## Possible improvements

Hybrid keyword + vector search (exact incident IDs are a keyword problem — `INC-1004` is best matched literally); reranking retrieved rows; a similarity-score floor; query rewriting; conversation memory; a Streamlit UI; swapping FAISS for SAP HANA Cloud Vector Engine; deployment to SAP BTP Cloud Foundry; and an evaluation set with expected answers plus automatic groundedness checks.

## Deliverables

| Required (section 13) | Where |
| --- | --- |
| Colab notebook | [SAP_Incident_Knowledge_Assistant_Colab.ipynb](SAP_Incident_Knowledge_Assistant_Colab.ipynb) |
| Sample Excel dataset | `sap_incidents.xlsx`, built by [create_dataset.py](create_dataset.py) |
| Data-preparation explanation | [Design considerations](#design-considerations), and `clean_incidents` |
| RAG architecture diagram | [Architecture](#architecture) |
| Row-to-document conversion logic | `row_to_text` / `rows_to_documents` |
| Vector-store implementation | `build_vector_store` |
| Final question-answering function | `ask_incident_rag` (Task 10), `answer_question` (Task 11) |
| Results for all mandatory questions | [demo_output.txt](demo_output.txt) |
| Retrieved documents | [demo_output.txt](demo_output.txt), Task 7 section |
| Limitations and future improvements | [below](#limitation-aggregation-and-how-this-project-addresses-it) |

## Results

[demo_output.txt](demo_output.txt) holds a full captured run: Tasks 1-8, all mandatory test questions, the analytical routing, and the Section 8 expected output — which reproduces as specified:

> The P1 SAP HANA incident that took the longest to resolve was INC-1006, which required 9 hours to reach a resolution. Source: sap_incidents.xlsx, Excel row 7. In this incident, the resolution involved correcting storage pressure and optimizing the workload to address performance degradation caused by a long-running savepoint and storage pressure.
