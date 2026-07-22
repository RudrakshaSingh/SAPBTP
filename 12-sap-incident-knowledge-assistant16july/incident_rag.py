"""SAP Incident Knowledge Assistant -- RAG over structured Excel data.

Pipeline
--------
1.  ``load_incidents``    Task 1  -- read sap_incidents.xlsx with Pandas.
2.  ``explore_incidents`` Task 1  -- shape, dtypes, missing values, distributions.
3.  ``clean_incidents``   Task 2  -- drop empty rows, normalise text/dates/numbers.
4.  ``rows_to_documents`` Task 3  -- one Excel row -> one LangChain Document.
5.  ``chunk_documents``   Task 4  -- row-aware chunking, only splits long records.
6.  ``build_vector_store`` Tasks 5-6 -- Gemini embeddings indexed in FAISS.
7.  ``retrieve``          Tasks 7-8 -- semantic search plus metadata filters.
8.  ``ask_incident_rag``  Tasks 9-10 -- grounded answer with source citations.
9.  ``answer_question``   Task 11 -- routes analytical questions to Pandas.

The Excel row number is captured before any row is dropped, so citations always
point at the real line in the workbook.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

load_dotenv()

# Model names are overridable via environment variables so the app keeps working
# as new Gemini versions are released.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/gemini-embedding-001")

EXCEL_FILE = "sap_incidents.xlsx"
SHEET_NAME = "incidents"

# A record longer than this is split; every row in this dataset stays well under
# it, so in practice one incident remains one chunk.
MAX_CHARS_PER_CHUNK = 1500
CHUNK_OVERLAP = 150

TEXT_COLUMNS = [
    "incident_id",
    "sap_module",
    "category",
    "priority",
    "issue_summary",
    "issue_description",
    "root_cause",
    "resolution",
    "owner_team",
    "status",
]

# Canonical spelling for every module, keyed by its normalised form. Excel data
# arrives as "  sap hana  ", "SAP Hana", "SAP HANA" and all must collapse to one
# value, otherwise a metadata filter on sap_module silently misses rows.
MODULE_CANON = {
    "sap mm": "SAP MM",
    "sap sd": "SAP SD",
    "sap hana": "SAP HANA",
    "sap btp": "SAP BTP",
    "sap successfactors": "SAP SuccessFactors",
}

MISSING_TEXT = "Not documented"


# --------------------------------------------------------------------------- #
# Task 1 -- load and explore
# --------------------------------------------------------------------------- #
def load_incidents(path: str = EXCEL_FILE, sheet: str = SHEET_NAME) -> pd.DataFrame:
    """Read the workbook and stamp each record with its true Excel row number.

    Row 1 holds the header, so the first data row is Excel row 2. This happens
    before cleaning because dropping rows would otherwise shift every citation.
    """
    df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    df["excel_row"] = df.index + 2
    df.attrs["source_name"] = os.path.basename(path)
    df.attrs["sheet_name"] = sheet
    return df


def explore_incidents(df: pd.DataFrame) -> None:
    """Print the Task 1 data-quality checks."""
    print("=" * 70)
    print("TASK 1 -- DATA EXPLORATION")
    print("=" * 70)

    print(f"\nRecords: {len(df)}   Columns: {len(df.columns)}")

    print("\nFirst five rows:")
    print(df.head().to_string())

    print("\nColumn names:")
    print(list(df.columns))

    print("\nData types:")
    print(df.dtypes.to_string())

    print("\nMissing values per column:")
    missing = df.isna().sum()
    print(missing[missing > 0].to_string() if missing.any() else "None")

    print("\nIncidents by SAP module:")
    print(df["sap_module"].value_counts(dropna=False).to_string())

    print("\nIncidents by priority:")
    print(df["priority"].value_counts(dropna=False).to_string())


# --------------------------------------------------------------------------- #
# Task 2 -- clean and prepare
# --------------------------------------------------------------------------- #
def _clean_text(value) -> str:
    """Strip padding, collapse runs of whitespace, drop control characters."""
    if pd.isna(value):
        return MISSING_TEXT
    text = str(value).replace(" ", " ")
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or MISSING_TEXT


def _canonical_module(value: str) -> str:
    return MODULE_CANON.get(value.strip().lower(), value.strip())


def _parse_dates(series: pd.Series) -> pd.Series:
    """Normalise mixed date formats to YYYY-MM-DD.

    The raw file holds both 2024-03-05 and 01-04-2024. Passing dayfirst=True over
    the whole column would reinterpret the ISO dates and silently swap day and
    month, so ISO is parsed strictly first and only the leftovers get dayfirst.
    """
    iso = pd.to_datetime(series, format="%Y-%m-%d", errors="coerce")
    remainder = pd.to_datetime(series[iso.isna()], errors="coerce", dayfirst=True)
    parsed = iso.fillna(remainder)
    return parsed.dt.strftime("%Y-%m-%d").fillna("Unknown")


def clean_incidents(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean dataframe ready to become LangChain documents."""
    print("\n" + "=" * 70)
    print("TASK 2 -- CLEANING")
    print("=" * 70)

    before = len(df)
    data_columns = [c for c in df.columns if c != "excel_row"]

    # Remove rows that carry no data at all.
    df = df.dropna(how="all", subset=data_columns).copy()
    print(f"\nDropped {before - len(df)} completely empty row(s).")

    for column in TEXT_COLUMNS:
        df[column] = df[column].map(_clean_text)

    df["sap_module"] = df["sap_module"].map(_canonical_module)
    df["priority"] = df["priority"].str.upper()
    df["status"] = df["status"].str.title()

    df["incident_date"] = _parse_dates(df["incident_date"])

    # Resolution time arrives as float in most rows and as text in others.
    df["resolution_time_hours"] = pd.to_numeric(
        df["resolution_time_hours"], errors="coerce"
    )

    # An incident with no ID cannot be cited, so it cannot be trusted.
    df = df[df["incident_id"] != MISSING_TEXT]

    df = df.reset_index(drop=True)
    print(f"Clean records: {len(df)}")
    print(f"Modules after normalisation: {sorted(df['sap_module'].unique())}")
    print(f"Priorities after normalisation: {sorted(df['priority'].unique())}")
    return df


# --------------------------------------------------------------------------- #
# Task 3 -- rows to documents
# --------------------------------------------------------------------------- #
def row_to_text(row: pd.Series) -> str:
    """Render one incident as the labelled text block the LLM will read.

    The field labels stay in the text on purpose: the embedding then carries the
    meaning of each value ("Root Cause: ...") rather than a bare string, and the
    model can quote the record back without guessing what a column means.
    """
    hours = row["resolution_time_hours"]
    hours_text = "Unknown" if pd.isna(hours) else f"{hours:g} hours"
    return (
        f"Incident ID: {row['incident_id']}\n"
        f"Incident Date: {row['incident_date']}\n"
        f"SAP Module: {row['sap_module']}\n"
        f"Priority: {row['priority']}\n"
        f"Category: {row['category']}\n"
        f"Issue Summary: {row['issue_summary']}\n"
        f"Issue Description: {row['issue_description']}\n"
        f"Root Cause: {row['root_cause']}\n"
        f"Resolution: {row['resolution']}\n"
        f"Owner Team: {row['owner_team']}\n"
        f"Resolution Time: {hours_text}\n"
        f"Status: {row['status']}"
    )


def rows_to_documents(df: pd.DataFrame) -> List[Document]:
    """Convert every cleaned Excel row into exactly one LangChain Document."""
    source_name = df.attrs.get("source_name", EXCEL_FILE)
    sheet_name = df.attrs.get("sheet_name", SHEET_NAME)

    documents = []
    for _, row in df.iterrows():
        documents.append(
            Document(
                page_content=row_to_text(row),
                metadata={
                    "source_type": "excel",
                    "source_name": source_name,
                    "sheet_name": sheet_name,
                    "row_number": int(row["excel_row"]),
                    "incident_id": row["incident_id"],
                    "sap_module": row["sap_module"],
                    "priority": row["priority"],
                    "category": row["category"],
                    "owner_team": row["owner_team"],
                },
            )
        )
    return documents


# --------------------------------------------------------------------------- #
# Task 4 -- row-aware chunking
# --------------------------------------------------------------------------- #
def chunk_documents(
    documents: List[Document], max_chars: int = MAX_CHARS_PER_CHUNK
) -> List[Document]:
    """Keep one incident as one chunk unless its text is genuinely too long.

    Fixed-size chunking would cut a record between "Root Cause" and "Resolution"
    and hand the retriever half an incident. Splitting only oversized records
    keeps each chunk a self-contained, citable unit.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chars,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n", ". ", " ", ""],
    )

    chunks: List[Document] = []
    split_count = 0
    for document in documents:
        incident_id = document.metadata["incident_id"]
        if len(document.page_content) <= max_chars:
            parts = [document]
        else:
            parts = splitter.split_documents([document])
            split_count += 1

        for index, part in enumerate(parts, start=1):
            part.metadata = {
                **document.metadata,
                "chunk_id": f"{incident_id}-chunk-{index}",
                "chunk_index": index,
                "chunk_total": len(parts),
            }
            chunks.append(part)

    print("\n" + "=" * 70)
    print("TASKS 3-4 -- DOCUMENTS AND CHUNKS")
    print("=" * 70)
    print(f"\nDocuments: {len(documents)}   Chunks: {len(chunks)}")
    print(f"Records that needed splitting: {split_count}")
    print(f"Longest record: {max(len(d.page_content) for d in documents)} chars")
    return chunks


# --------------------------------------------------------------------------- #
# Tasks 5-6 -- embeddings and vector store
# --------------------------------------------------------------------------- #
def build_vector_store(chunks: List[Document]) -> FAISS:
    """Embed the incident chunks with Gemini and index them in FAISS."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)

    probe = embeddings.embed_query("HANA database performance issue")
    print("\n" + "=" * 70)
    print("TASKS 5-6 -- EMBEDDINGS AND VECTOR STORE")
    print("=" * 70)
    print(f"\nEmbedding model: {EMBED_MODEL}")
    print(f"Test question vector length: {len(probe)}")
    print(f"First five dimensions: {[round(v, 4) for v in probe[:5]]}")

    store = FAISS.from_documents(chunks, embeddings)
    print(f"Indexed {store.index.ntotal} vectors in FAISS.")
    return store


# --------------------------------------------------------------------------- #
# Tasks 7-8 -- retrieval with metadata filtering
# --------------------------------------------------------------------------- #
@dataclass
class RetrievedIncident:
    """One retrieval hit, flattened for display and prompting."""

    rank: int
    score: float
    text: str
    metadata: dict

    @property
    def incident_id(self) -> str:
        return self.metadata["incident_id"]

    @property
    def row_number(self) -> int:
        return self.metadata["row_number"]


def retrieve(
    store: FAISS,
    question: str,
    top_k: int = 5,
    sap_module: Optional[str] = None,
    priority: Optional[str] = None,
    owner_team: Optional[str] = None,
) -> List[RetrievedIncident]:
    """Semantic search, optionally narrowed by structured metadata.

    Filters are applied inside the vector store, so "P1 SAP BTP incidents" can
    never return a P2 record that merely reads like one.
    """
    filters: Dict[str, str] = {}
    if sap_module:
        filters["sap_module"] = _canonical_module(sap_module)
    if priority:
        filters["priority"] = priority.strip().upper()
    if owner_team:
        filters["owner_team"] = owner_team.strip()

    # FAISS filters after the search, so fetch a wider candidate pool first.
    hits = store.similarity_search_with_score(
        question,
        k=top_k,
        filter=filters or None,
        fetch_k=max(50, top_k * 10),
    )
    return [
        RetrievedIncident(rank=i, score=float(score), text=doc.page_content, metadata=doc.metadata)
        for i, (doc, score) in enumerate(hits, start=1)
    ]


def print_retrieval(question: str, results: List[RetrievedIncident], show_text: bool = True) -> None:
    """Display Task 7's required fields for every hit."""
    print(f"\nQuery: {question}")
    if not results:
        print("  No incidents matched.")
        return
    for hit in results:
        print(f"\n  Rank {hit.rank} | score (L2 distance, lower is closer): {hit.score:.4f}")
        print(f"  Incident: {hit.incident_id} | Module: {hit.metadata['sap_module']} "
              f"| Priority: {hit.metadata['priority']} | Excel row: {hit.row_number}")
        print(f"  Chunk ID: {hit.metadata['chunk_id']}")
        if show_text:
            for line in hit.text.splitlines():
                print(f"      {line}")


# --------------------------------------------------------------------------- #
# Task 9 -- the grounded prompt
# --------------------------------------------------------------------------- #
FALLBACK = (
    "I could not find sufficient information in the incident dataset to "
    "answer this question."
)

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the SAP Incident Knowledge Assistant. You answer support "
            "engineers using ONLY the historical incident records supplied in "
            "the context.\n\n"
            "Rules:\n"
            "1. Use only the retrieved records. Never invent an incident, a "
            "root cause, a resolution, a team or a number.\n"
            "2. Name the incident ID for every fact you state.\n"
            "3. Mention the SAP module and the priority of each incident you use.\n"
            "4. Explain the resolution steps that were actually recorded.\n"
            "5. Cite the source as: Source: {source_name}, Excel row <number>.\n"
            "6. If the context does not contain the answer, reply exactly with:\n"
            "   {fallback}\n"
            "   Do not add anything else in that case.\n"
            "7. If the question asks for something the incident data does not "
            "track at all, use the same fallback sentence.\n"
            "Answer in plain prose. Be concise and specific.",
        ),
        (
            "human",
            "Retrieved incident records:\n"
            "---------------------------\n"
            "{context}\n"
            "---------------------------\n\n"
            "Question: {question}",
        ),
    ]
)


def format_context(results: List[RetrievedIncident]) -> str:
    """Render retrieved records, each tagged with its citation coordinates."""
    blocks = []
    for hit in results:
        blocks.append(
            f"[Record {hit.rank}] "
            f"(source: {hit.metadata['source_name']}, sheet: {hit.metadata['sheet_name']}, "
            f"Excel row: {hit.row_number}, chunk: {hit.metadata['chunk_id']})\n"
            f"{hit.text}"
        )
    return "\n\n".join(blocks)


# --------------------------------------------------------------------------- #
# Task 10 -- the final RAG function
# --------------------------------------------------------------------------- #
@dataclass
class RagAnswer:
    """A grounded answer plus the records it was built from."""

    question: str
    answer: str
    sources: List[RetrievedIncident]
    route: str = "semantic"

    def display(self) -> None:
        print(f"\nQ: {self.question}")
        print(f"   [route: {self.route}]")
        print(f"\nA: {self.answer}")
        if self.sources:
            print("\n   Sources used:")
            for hit in self.sources:
                print(
                    f"     - {hit.incident_id} | {hit.metadata['sap_module']} "
                    f"| {hit.metadata['priority']} | {hit.metadata['source_name']} "
                    f"row {hit.row_number}"
                )
        print("-" * 70)


def _chat_model() -> ChatGoogleGenerativeAI:
    # temperature=0 keeps the answer pinned to the retrieved text.
    return ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)


def _response_text(response) -> str:
    """Flatten a chat response to plain text.

    ``content`` is a plain string on most replies but a list of content blocks
    on others, so both shapes have to be handled.
    """
    content = response.content
    if isinstance(content, str):
        return content.strip()
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts).strip()


def ask_incident_rag(
    question: str,
    store: FAISS,
    top_k: int = 5,
    sap_module: Optional[str] = None,
    priority: Optional[str] = None,
    owner_team: Optional[str] = None,
) -> RagAnswer:
    """Answer a question from the incident history, grounded in retrieved rows."""
    results = retrieve(
        store,
        question,
        top_k=top_k,
        sap_module=sap_module,
        priority=priority,
        owner_team=owner_team,
    )

    if not results:
        return RagAnswer(question=question, answer=FALLBACK, sources=[])

    chain = RAG_PROMPT | _chat_model()
    response = chain.invoke(
        {
            "context": format_context(results),
            "question": question,
            "fallback": FALLBACK,
            "source_name": results[0].metadata["source_name"],
        }
    )
    return RagAnswer(question=question, answer=_response_text(response), sources=results)


# --------------------------------------------------------------------------- #
# Task 11 -- route analytical questions to Pandas
# --------------------------------------------------------------------------- #
class Route(BaseModel):
    """Which engine should answer this question."""

    route: str = Field(
        description=(
            "'analytical' when the question needs a calculation over ALL "
            "incidents -- counts, averages, totals, min/max across the dataset, "
            "or ranking every module. 'semantic' when the question is about the "
            "content of specific incidents, their causes or resolutions."
        )
    )
    reason: str = Field(description="One short sentence explaining the choice.")


ANALYTICAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You answer questions about an SAP incident dataset using ONLY the "
            "pre-computed statistics below. They were calculated with Pandas over "
            "every row, so they are exact -- quote the numbers as given and do "
            "not recompute or estimate. If the statistics do not contain the "
            "answer, reply exactly with:\n{fallback}\n"
            "Cite the dataset as: Source: {source_name} (computed with Pandas "
            "over all rows). Be concise.",
        ),
        (
            "human",
            "Dataset statistics:\n"
            "-------------------\n"
            "{stats}\n"
            "-------------------\n\n"
            "Question: {question}",
        ),
    ]
)


def classify_question(question: str) -> Route:
    """Decide whether vector RAG or Pandas should handle the question."""
    model = _chat_model().with_structured_output(Route)
    return model.invoke(
        "Classify this question about an SAP incident dataset as 'analytical' "
        f"or 'semantic'.\n\nQuestion: {question}"
    )


def compute_statistics(df: pd.DataFrame) -> str:
    """Exact aggregates from Pandas -- the numbers vector search cannot give.

    Retrieval returns the top-k most similar rows, never "all of them", so any
    count or average built from retrieved context is wrong by construction. These
    are computed over the full dataframe instead.
    """
    lines = [f"Total incidents: {len(df)}", ""]

    lines.append("Incident count by priority:")
    for priority, count in df["priority"].value_counts().sort_index().items():
        lines.append(f"  {priority}: {count}")

    lines.append("\nIncident count by SAP module:")
    for module, count in df["sap_module"].value_counts().items():
        lines.append(f"  {module}: {count}")

    lines.append("\nResolution time (hours) by SAP module:")
    stats = df.groupby("sap_module")["resolution_time_hours"].agg(["mean", "max", "sum", "count"])
    for module, row in stats.iterrows():
        lines.append(
            f"  {module}: average {row['mean']:.2f}, longest {row['max']:.2f}, "
            f"total {row['sum']:.2f}, incidents {int(row['count'])}"
        )

    lines.append("\nResolution time (hours) by priority:")
    stats = df.groupby("priority")["resolution_time_hours"].agg(["mean", "max", "count"])
    for priority, row in stats.sort_index().iterrows():
        lines.append(
            f"  {priority}: average {row['mean']:.2f}, longest {row['max']:.2f}, "
            f"incidents {int(row['count'])}"
        )

    slowest = df.loc[df["resolution_time_hours"].idxmax()]
    lines.append(
        f"\nLongest incident overall: {slowest['incident_id']} "
        f"({slowest['sap_module']}, {slowest['priority']}, "
        f"{slowest['resolution_time_hours']:g} hours, Excel row {slowest['excel_row']})"
    )

    lines.append("\nEvery incident (id | module | priority | hours | Excel row):")
    for _, row in df.iterrows():
        hours = row["resolution_time_hours"]
        hours_text = "unknown" if pd.isna(hours) else f"{hours:g}"
        lines.append(
            f"  {row['incident_id']} | {row['sap_module']} | {row['priority']} "
            f"| {hours_text} | row {row['excel_row']}"
        )

    return "\n".join(lines)


def ask_analytical(question: str, df: pd.DataFrame) -> RagAnswer:
    """Answer a calculation question from Pandas aggregates."""
    chain = ANALYTICAL_PROMPT | _chat_model()
    response = chain.invoke(
        {
            "stats": compute_statistics(df),
            "question": question,
            "fallback": FALLBACK,
            "source_name": df.attrs.get("source_name", EXCEL_FILE),
        }
    )
    return RagAnswer(
        question=question,
        answer=_response_text(response),
        sources=[],
        route="analytical (Pandas)",
    )


def answer_question(
    question: str,
    store: FAISS,
    df: pd.DataFrame,
    top_k: int = 5,
    **filters,
) -> RagAnswer:
    """Front door: classify the question, then send it to RAG or to Pandas."""
    if filters.get("sap_module") or filters.get("priority") or filters.get("owner_team"):
        # An explicit filter means the caller already wants record lookup.
        return ask_incident_rag(question, store, top_k=top_k, **filters)

    route = classify_question(question)
    if route.route == "analytical":
        return ask_analytical(question, df)
    return ask_incident_rag(question, store, top_k=top_k, **filters)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_assistant(path: str = EXCEL_FILE, verbose: bool = True):
    """Run the whole pipeline and return the vector store plus clean dataframe."""
    raw = load_incidents(path)
    if verbose:
        explore_incidents(raw)

    clean = clean_incidents(raw)
    clean.attrs.update(raw.attrs)

    documents = rows_to_documents(clean)
    chunks = chunk_documents(documents)

    if verbose:
        print("\nExample document (INC-1006):")
        for doc in documents:
            if doc.metadata["incident_id"] == "INC-1006":
                print(doc.page_content)
                print(f"\nMetadata: {doc.metadata}")
                break

    store = build_vector_store(chunks)
    return store, clean
