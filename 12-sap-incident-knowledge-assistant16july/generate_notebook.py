"""Build the Colab notebook from the real source files.

The notebook is generated rather than hand-written so its code can never drift
away from incident_rag.py / create_dataset.py -- the modules stay the single
source of truth, and the notebook is a rendered view of them.

Run:
    python generate_notebook.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

NOTEBOOK = Path("SAP_Incident_Knowledge_Assistant_Colab.ipynb")

BANNER = re.compile(r"^# -{20,} #\n# (.+?)\n# -{20,} #\n", re.MULTILINE)


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip().splitlines(keepends=True),
    }


def strip_docstring(source: str) -> str:
    """Drop the leading module docstring -- the notebook says it in markdown."""
    match = re.match(r'\s*""".*?"""\s*', source, re.DOTALL)
    return source[match.end():] if match else source


def split_sections(source: str) -> list[tuple[str, str]]:
    """Split a module into (banner title, body) pairs.

    The text before the first banner is returned under the title 'Setup'.
    """
    parts = BANNER.split(source)
    sections = [("Setup", parts[0])]
    for i in range(1, len(parts), 2):
        sections.append((parts[i], parts[i + 1]))
    return sections


# Markdown that introduces each section of incident_rag.py, keyed by banner title.
NOTES = {
    "Setup": """
## Imports and configuration

`GEMINI_CHAT_MODEL` and `GEMINI_EMBED_MODEL` are read from the environment so the
notebook keeps working as new Gemini versions ship.

`MODULE_CANON` matters more than it looks: the raw sheet contains `"  sap hana  "`
as well as `"SAP HANA"`. Left alone, that row becomes invisible to a
`sap_module="SAP HANA"` filter forever.
""",
    "Task 1 -- load and explore": """
## Task 1 — Load and explore the Excel data

The important line is `df["excel_row"] = df.index + 2`.

Row 1 of the workbook is the header, so the first incident sits on Excel row 2.
The row number is stamped **before any cleaning**, because dropping the empty row
later would shift every subsequent row and silently corrupt every citation.
""",
    "Task 2 -- clean and prepare": """
## Task 2 — Clean and prepare the data

The raw sheet is deliberately messy, and each defect maps to a fix:

| Defect in the sheet | Fix |
| --- | --- |
| A completely empty row | `dropna(how="all")` |
| `"  sap hana  "` | `_canonical_module` → `SAP HANA` |
| `"p2"` | `.str.upper()` → `P2` |
| `"2.75"` stored as text | `pd.to_numeric` |
| A missing root cause | default `"Not documented"` |
| `2024-03-05` mixed with `01-04-2024` | `_parse_dates` |

`_parse_dates` deserves a note. Passing `dayfirst=True` across the whole column
would reinterpret the ISO dates and swap day for month — `2024-03-05` would
silently become 3 May. So ISO is parsed strictly first, and only the leftovers
get `dayfirst`.
""",
    "Task 3 -- rows to documents": """
## Task 3 — Convert Excel rows into documents

**One row becomes exactly one `Document`.** A row *is* the unit of meaning: the
symptom, the root cause, the fix and the team only make sense together, and
`"Expired destination credentials"` is useless without the symptom it explains.

The field labels stay in the text on purpose. The embedding then carries the
meaning of each value (`Root Cause: ...`) rather than a bare string, and the model
can quote the record back without guessing what a column meant.

The structured fields are *also* kept as metadata, which is what makes filtering
and citation possible later.
""",
    "Task 4 -- row-aware chunking": """
## Task 4 — Row-aware chunking

Fixed-size chunking would wreck this data. A 500-character window over the sheet
would cut between `Root Cause:` and `Resolution:`, or merge the tail of INC-1004
with the head of INC-1005. Two concrete failures follow:

- **Severed fields** — a chunk with a root cause but no resolution retrieves well
  and answers nothing.
- **Blended records** — a chunk spanning two incidents lets the model attribute
  INC-1005's fix to INC-1004. That is a hallucination handed to it by retrieval.

So a record is split **only** if it exceeds ~1,500 characters. The longest row here
is 587 characters, so all 20 stay intact — the splitter is insurance for one
unusually verbose incident, not the normal path.
""",
    "Tasks 5-6 -- embeddings and vector store": """
## Tasks 5 & 6 — Embeddings and the vector database

`gemini-embedding-001` turns each incident into a 3,072-dimension vector, and FAISS
indexes them alongside the text and metadata.

The `embed_query("HANA database performance issue")` probe is the Task 5 sanity
check: it proves a question and a record land in the same vector space.
""",
    "Tasks 7-8 -- retrieval with metadata filtering": """
## Tasks 7 & 8 — Semantic retrieval and metadata filtering

**Task 7** is vector search: it matches *meaning*, not characters.

**Task 8** is the filter, and the two do different jobs. Similarity is a soft
signal, so "only P1" is not enforceable by embeddings — a P2 incident that *reads*
like a crisis can out-rank a terse P1. Priority is a recorded fact, so filtering on
metadata makes it a hard constraint and leaves similarity to do what it is good at:
ranking the survivors.

FAISS applies filters *after* the search, so `fetch_k` widens the candidate pool
first.

Scores are **L2 distances — lower is closer**, the opposite of a similarity score.
""",
    "Task 9 -- the grounded prompt": """
## Task 9 — The grounded prompt

Four anti-hallucination mechanisms stack here:

1. **Closed-book instruction** — use only the retrieved records; never invent an
   incident, cause, team or number.
2. **A mandatory fallback** — one fixed sentence when the context falls short, so
   refusal is an easy explicit path rather than a failure the model improvises
   around.
3. **Forced citation** — every claim carries an incident ID and Excel row. A
   fabricated fact has no row to cite, and any slip is auditable by the reader.
4. **`temperature=0`** — no sampling creativity in what is really a lookup task.
""",
    "Task 10 -- the final RAG function": """
## Task 10 — The final RAG function

`ask_incident_rag(question, store, top_k=5, sap_module=None, priority=None)`
retrieves, formats the context, prompts Gemini, and returns the answer together
with the records it was built from.

`_response_text` handles both shapes of `response.content`: a plain string on most
replies, a list of content blocks on others.
""",
    "Task 11 -- route analytical questions to Pandas": """
## Task 11 — Routing analytical questions to Pandas

**This is the limitation the problem statement asks you to address.**

*"How many P1 incidents were reported?"* is unanswerable by retrieval, by
construction. Top-k returns 5 rows; the answer is 6. The model would faithfully
count what it was given and confidently report **5** — grounded in its context and
still wrong. Averages fail worse: an average over the 5 most *similar* rows is an
average over a biased sample nobody asked for.

The fix is not a better prompt, it is a different engine. `compute_statistics` runs
Pandas over the **whole** dataframe and Gemini only phrases the exact numbers.
Both branches keep the same fallback sentence, so refusal behaviour holds either
way.
""",
    "Assembly": """
## Assembly

`build_assistant` runs Tasks 1–6 and hands back the vector store plus the clean
dataframe — the store for semantic questions, the dataframe for analytical ones.
""",
}


def build_cells() -> list[dict]:
    cells: list[dict] = [
        md("""
# SAP Incident Knowledge Assistant

## RAG over structured Excel data, with Google Gemini

Support engineers search a historical incident spreadsheet by hand. It is slow when
the sheet has thousands of rows, when nobody remembers the incident ID, and when a
past incident described the same problem in different words.

This notebook builds a RAG application over that spreadsheet. Ask a question in
plain English, get an answer grounded **only** in the incident history, with the
incident ID and Excel row number cited for every claim.

### What you will build

| Task | Step |
| --- | --- |
| 1–2 | Load and clean the Excel data with Pandas |
| 3 | Turn one Excel row into one LangChain `Document` |
| 4 | Row-aware chunking that keeps records intact |
| 5–6 | Gemini embeddings indexed in FAISS |
| 7–8 | Semantic retrieval + metadata filtering |
| 9–10 | A grounded prompt and the final RAG function |
| 11 | Route calculations to Pandas instead of RAG |
"""),
        md("""
## Architecture

```text
sap_incidents.xlsx  (one incident per row)
        |
        |  Task 1-2   Pandas: load, stamp Excel row number, clean
        v
  Clean dataframe ------------------------------+
        |                                       |
        |  Task 3     one row -> one Document   |
        v             (labelled text + metadata)|
  LangChain Documents                           |
        |                                       |
        |  Task 4     split only if oversized   |
        v                                       |
     Chunks                                     |
        |                                       |
        |  Task 5-6   Gemini embeddings         |
        v                                       |
   FAISS vector store                           |
        |                                       |
        +---------------+-----------------------+
                        |
                  User question
                        |
                        v
              Question classification            (Task 11)
                        |
        +---------------+----------------+
        |                                |
  Semantic question               Analytical question
        |                                |
  Tasks 7-8                       Pandas aggregates
  vector search                   over ALL rows
  + metadata filter                      |
        |                                |
        v                                v
  Retrieved records                 Exact statistics
        |                                |
        +---------------+----------------+
                        |
                  Task 9 grounded prompt
                        v
                  Google Gemini
                        |
                        v
        Answer + incident IDs + Excel row citations
```
"""),
        md("""
## Setup

Install the dependencies, then supply a Gemini API key. Get one free at
[aistudio.google.com/apikey](https://aistudio.google.com/apikey).

In Colab, store it as a secret named `GOOGLE_API_KEY` (the key icon in the left
sidebar) and the next cell will pick it up. Otherwise it will prompt you.
"""),
        code("""
%pip install -q langchain langchain-core langchain-community langchain-google-genai \\
    langchain-text-splitters faiss-cpu pandas openpyxl pydantic python-dotenv
"""),
        code('''
import os

def _load_api_key() -> None:
    """Read the key from Colab secrets, the environment, or a prompt."""
    if os.getenv("GOOGLE_API_KEY"):
        print("Using GOOGLE_API_KEY from the environment.")
        return
    try:
        from google.colab import userdata

        os.environ["GOOGLE_API_KEY"] = userdata.get("GOOGLE_API_KEY")
        print("Using GOOGLE_API_KEY from Colab secrets.")
        return
    except Exception:
        pass

    from getpass import getpass

    os.environ["GOOGLE_API_KEY"] = getpass("Enter your GOOGLE_API_KEY: ")
    print("Key set for this session.")

_load_api_key()
'''),
        md("""
## The dataset

`sap_incidents.xlsx` holds 20 resolved incidents across SAP MM, SD, HANA, BTP and
SuccessFactors.

The first eight rows are the sample data from the problem statement, so **INC-1006
lands on Excel row 7** exactly as the expected output requires. Some later rows are
deliberately messy — an empty row, padded whitespace, a lower-case priority, a
number stored as text, a missing root cause — so that the cleaning step has real
work to do.
"""),
        code(strip_docstring(Path("create_dataset.py").read_text(encoding="utf-8"))
             .replace('if __name__ == "__main__":\n    main()', "main()")),
    ]

    for title, body in split_sections(
        strip_docstring(Path("incident_rag.py").read_text(encoding="utf-8"))
    ):
        note = NOTES.get(title)
        if note:
            cells.append(md(note))
        cells.append(code(body))

    cells.extend(
        [
            md("""
## Run the pipeline

Tasks 1–6 end to end: load, explore, clean, convert to documents, chunk, embed and
index.
"""),
            code("store, df = build_assistant()"),
            md("""
## Task 7 — Semantic retrieval

Note the wording of these questions: it deliberately differs from the text in the
sheet. *"HANA memory exhaustion"* is not a phrase any row contains, yet INC-1002
ranks first — because the embedding matches meaning, not characters. A keyword
search for that phrase returns nothing.
"""),
            code('''
for question in [
    "Which incident was related to HANA memory exhaustion?",
    "Find incidents involving SAP BTP connectivity problems.",
    "Which issue was caused by an incorrect pricing procedure?",
    "Show incidents related to employee integration failures.",
]:
    print_retrieval(question, retrieve(store, question, top_k=3))
'''),
            md("""
## Task 8 — Metadata filtering

The filter is a hard constraint: a non-P1 row is now structurally unreachable, no
matter how similar it reads.
"""),
            code('''
for question, filters in [
    ("Show the most critical incidents.", {"priority": "P1"}),
    ("Database problems.", {"sap_module": "SAP HANA"}),
    ("Access and connection issues.",
     {"sap_module": "SAP BTP", "owner_team": "BTP Platform Team"}),
]:
    print(f"\\nFilters: {filters}")
    print_retrieval(question, retrieve(store, question, top_k=3, **filters),
                    show_text=False)
'''),
            md("""
## Mandatory test questions

Every question from section 7 of the problem statement — factual, semantic,
comparison, filter-based, recommendation-style, and one the data cannot answer.

`answer_question` classifies each one first, so watch the `[route: ...]` line:
*"Which P1 incident took the longest time to resolve?"* is a calculation and goes
to Pandas, while the rest go to vector RAG.
"""),
            code('''
MANDATORY_QUESTIONS = [
    # Direct factual
    ("What was the resolution for incident INC-1004?", {}),
    ("Which team resolved the employee replication issue?", {}),
    # Semantic
    ("Has there been an issue where a cloud application could not connect to an SAP backend?", {}),
    ("Find a previous incident involving database memory problems.", {}),
    # Comparison
    ("Which P1 incident took the longest time to resolve?", {}),
    ("Compare the two SAP HANA P1 incidents.", {}),
    # Filter-based
    ("Show only P1 SAP BTP incidents.", {"sap_module": "SAP BTP", "priority": "P1"}),
    ("Find SAP MM incidents handled by the Procure-to-Pay Support team.",
     {"sap_module": "SAP MM", "owner_team": "Procure-to-Pay Support"}),
    # Recommendation-style
    ("A user reports that a BTP application cannot access the backend because "
     "authentication is failing. Which previous incident is most similar, and "
     "what resolution should the support team investigate?", {}),
    # Unsupported -- must refuse rather than invent
    ("What is the annual revenue of the company?", {}),
]

for question, filters in MANDATORY_QUESTIONS:
    answer_question(question, store, df, **filters).display()
'''),
            md("""
### The unsupported question

The dataset tracks incidents, not finances, so *"What is the annual revenue of the
company?"* returns the fallback sentence rather than a guess. That refusal is the
grounded prompt working.
"""),
            md("""
## Section 11 — Analytical questions

These are the questions vector retrieval alone gets *confidently wrong*. Each is
routed to Pandas and computed over every row.

You can verify the numbers yourself in the cell below.
"""),
            code('''
for question in [
    "What is the average resolution time for SAP HANA incidents?",
    "How many P1 incidents were reported?",
    "Which module has the highest average resolution time?",
]:
    answer_question(question, store, df).display()
'''),
            code('''
# Check the LLM's numbers against Pandas directly.
print("Average resolution time by module:")
print(df.groupby("sap_module")["resolution_time_hours"].mean().round(2).to_string())
print("\\nP1 incidents:", (df["priority"] == "P1").sum())
'''),
            md("""
## Section 8 — Expected final output

The worked example from the problem statement. Expected: INC-1006, 9 hours,
`sap_incidents.xlsx` Excel row 7.
"""),
            code('''
ask_incident_rag(
    "Which P1 SAP HANA incident took the longest to resolve?",
    store,
    sap_module="SAP HANA",
    priority="P1",
).display()
'''),
            md("""
## Limitations and future improvements

**Aggregation at scale.** The Pandas branch works here because 20 incidents
summarise into the prompt. At thousands of rows that digest stops fitting in the
context window, and the aggregate step should become a real tool call — a
`pandas.query` tool or SQL — with the LLM writing the query instead of reading a
pre-computed digest.

**Other known limits**

- Retrieval has no score threshold: every query returns `top_k` rows even when
  nothing is relevant. The grounded prompt catches this at the answer stage, but a
  distance floor would stop weak context being sent at all.
- The classifier is one LLM call with no fallback; a misrouted count answers from 5
  rows without saying so.
- FAISS filters post-search, so on a much larger sheet a narrow filter could exhaust
  the candidate pool. Chroma's native `where` clause would scale better.
- Filters are exact-match only — no ranges (`resolution_time_hours > 5`), no OR.
- No conversation memory: *"and who fixed that one?"* will not resolve.
- The index rebuilds on every run; `FAISS.save_local` would persist it.

**Worth adding next:** hybrid keyword + vector search (an exact ID like `INC-1004`
is really a keyword problem), reranking, query rewriting, conversation memory, a
Streamlit UI, SAP HANA Cloud Vector Engine in place of FAISS, deployment to SAP BTP
Cloud Foundry, and an evaluation set with automatic groundedness checks.
"""),
        ]
    )
    return cells


def main() -> None:
    notebook = {
        "cells": build_cells(),
        "metadata": {
            "colab": {"name": NOTEBOOK.name, "provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    counts = {"markdown": 0, "code": 0}
    for cell in notebook["cells"]:
        counts[cell["cell_type"]] += 1
    print(f"Wrote {NOTEBOOK} -- {counts['markdown']} markdown + {counts['code']} code cells.")


if __name__ == "__main__":
    main()
