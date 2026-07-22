"""Deterministic tools the Resume-to-Job Match agent can call.

Three plain Python functions do the work that does not need an LLM:

1.  ``normalize_skill``        -- one canonical name per skill ("BTP" -> "SAP BTP").
2.  ``calculate_fit_score``    -- weighted 0-100 score from the matched/missing lists.
3.  ``generate_learning_plan`` -- a 30/60/90 day roadmap for the missing skills.

Keeping these out of the LLM matters: a score that comes from a prompt changes
every run, while a score that comes from arithmetic can be explained, tested and
argued with. The bottom of the file also wraps them as LangChain tools
(``MATCH_TOOLS``) for the advanced tool-calling challenge.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence, Set

from langchain_core.tools import tool as as_tool

# --------------------------------------------------------------------------- #
# SAP + GenAI skill taxonomy
# --------------------------------------------------------------------------- #

# Every spelling a resume or job ad might use, mapped to one canonical name.
# Without this, "CPI" in the JD and "SAP Integration Suite" in the resume look
# like two different skills, and the candidate is marked down for a gap that
# does not exist.
SKILL_SYNONYMS: Dict[str, str] = {
    # --- SAP platform ---
    "btp": "SAP BTP",
    "sap business technology platform": "SAP BTP",
    "business technology platform": "SAP BTP",
    "cpi": "SAP Integration Suite",
    "sap cpi": "SAP Integration Suite",
    "cloud integration": "SAP Integration Suite",
    "integration suite": "SAP Integration Suite",
    "pi po": "SAP Integration Suite",
    "cap": "SAP CAP",
    "cloud application programming model": "SAP CAP",
    "cap applications": "SAP CAP",
    "rap": "SAP RAP",
    "restful application programming model": "SAP RAP",
    "abap": "ABAP",
    "abap cloud": "ABAP Cloud",
    "hana": "SAP HANA Cloud",
    "sap hana": "SAP HANA Cloud",
    "hana cloud": "SAP HANA Cloud",
    "hana vector engine": "SAP HANA Cloud Vector Engine",
    "vector engine": "SAP HANA Cloud Vector Engine",
    "bpa": "SAP Build Process Automation",
    "build process automation": "SAP Build Process Automation",
    "workflow management": "SAP Build Process Automation",
    "build apps": "SAP Build Apps",
    "fiori": "SAP Fiori",
    "ui5": "SAP Fiori",
    "s4hana": "SAP S/4HANA",
    "s 4hana": "SAP S/4HANA",
    "successfactors": "SAP SuccessFactors",
    # --- SAP AI ---
    "ai core": "SAP AI Core",
    "sap ai core": "SAP AI Core",
    "ai launchpad": "SAP AI Launchpad",
    "sap gen ai": "SAP Generative AI Hub",
    "sap genai": "SAP Generative AI Hub",
    "gen ai hub": "SAP Generative AI Hub",
    "genai hub": "SAP Generative AI Hub",
    "generative ai hub": "SAP Generative AI Hub",
    "joule": "SAP Joule",
    "joule studio": "SAP Joule",
    "sap business ai": "SAP Business AI",
    # --- Generative / agentic AI ---
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "llm": "Generative AI",
    "llms": "Generative AI",
    "large language models": "Generative AI",
    "retrieval augmented generation": "RAG",
    "graph rag": "GraphRAG",
    "agentic ai": "Agentic AI",
    "ai agents": "Agentic AI",
    "agentic workflows": "Agentic AI",
    "multi agent": "Agentic AI",
    "langgraph": "LangGraph",
    "langchain": "LangChain",
    "prompt engineering": "Prompt Engineering",
    "vector db": "Vector Database",
    "vector database": "Vector Database",
    "vector store": "Vector Database",
    "embeddings": "Embeddings",
    "fine tuning": "Fine-tuning",
    # --- general engineering ---
    "python": "Python",
    "sql": "SQL",
    "rest api": "REST APIs",
    "odata": "OData",
    "javascript": "JavaScript",
    "node js": "Node.js",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "spark": "Apache Spark",
    "airflow": "Apache Airflow",
    "etl": "ETL",
    "data modeling": "Data Modelling",
    "data modelling": "Data Modelling",
}

# The canonical names are valid inputs too, so "SAP BTP" normalises to itself
# rather than falling through to the "unknown skill" branch.
SKILL_SYNONYMS.update({name.lower(): name for name in set(SKILL_SYNONYMS.values())})

# The two buckets the scoring rubric weights separately.
SAP_PLATFORM_SKILLS: Set[str] = {
    "SAP BTP", "SAP Integration Suite", "SAP CAP", "SAP RAP", "ABAP", "ABAP Cloud",
    "SAP HANA Cloud", "SAP HANA Cloud Vector Engine", "SAP Build Process Automation",
    "SAP Build Apps", "SAP Fiori", "SAP S/4HANA", "SAP SuccessFactors", "SAP AI Core",
    "SAP AI Launchpad", "SAP Generative AI Hub", "SAP Joule", "SAP Business AI",
}

GENAI_SKILLS: Set[str] = {
    "Generative AI", "RAG", "GraphRAG", "Agentic AI", "LangGraph", "LangChain",
    "Prompt Engineering", "Vector Database", "Embeddings", "Fine-tuning",
    "SAP Generative AI Hub", "SAP AI Core", "SAP Joule",
}

# Section 6 of the problem statement -- the weight each area carries out of 100.
WEIGHTS: Dict[str, int] = {
    "core_technical": 40,
    "sap_btp_experience": 20,
    "genai_experience": 20,
    "project_relevance": 10,
    "consulting_fit": 10,
}

# A skill the candidate half-covers counts as half a match everywhere.
PARTIAL_CREDIT = 0.5

# Fit bands. The router in job_match_agent.py reads the same numbers.
STRONG_FIT = 80
MEDIUM_FIT = 60


# --------------------------------------------------------------------------- #
# Tool 1 -- skill normalizer
# --------------------------------------------------------------------------- #
def normalize_skill(skill: str) -> str:
    """Normalize similar skill names onto one canonical form.

    Example: ``SAP Gen AI`` -> ``SAP Generative AI Hub``, ``BTP`` -> ``SAP BTP``,
    ``CPI`` -> ``SAP Integration Suite``.

    Unknown skills are returned trimmed but otherwise untouched -- the taxonomy
    is a helper, not a whitelist, so a job asking for Terraform still works.
    """
    # Punctuation is dropped so "SAP AI Core," / "(CPI)" / "Node.js" all land on
    # the same lookup key as their clean spelling.
    key = " ".join(re.sub(r"[^a-z0-9+#]+", " ", skill.lower()).split())
    if key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[key]
    # "SAP LangGraph" style prefixes: try again without the leading vendor word.
    if key.startswith("sap ") and key[4:] in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[key[4:]]
    return skill.strip()


def normalize_skills(skills: Iterable[str]) -> List[str]:
    """Normalize a whole list and drop duplicates, keeping the original order."""
    seen: List[str] = []
    for skill in skills or []:
        canonical = normalize_skill(skill)
        if canonical and canonical not in seen:
            seen.append(canonical)
    return seen


# --------------------------------------------------------------------------- #
# Tool 2 -- fit score calculator
# --------------------------------------------------------------------------- #
def score_breakdown(
    matched_skills: Sequence[str],
    missing_skills: Sequence[str],
    required_skills: Sequence[str],
    partially_matched_skills: Sequence[str] = (),
    projects: Sequence[str] = (),
) -> Dict[str, int]:
    """Return the per-area points behind the fit score.

    The rubric is tuned for SAP BTP + Generative AI roles: a job that asks for
    nothing from the SAP stack scores zero in that area by design, which is why
    the same resume scores lower against a Data Engineer advert.
    """
    required = set(normalize_skills(required_skills))
    matched = set(normalize_skills(matched_skills))
    partial = set(normalize_skills(partially_matched_skills))

    def covered(pool: Set[str]) -> float:
        """Weighted count of a pool of required skills the candidate covers."""
        return len(matched & pool) + PARTIAL_CREDIT * len(partial & pool)

    def share(pool: Set[str]) -> float:
        """Fraction of ``pool`` covered; 0.0 when the job does not ask for any."""
        return covered(pool) / len(pool) if pool else 0.0

    # Area 1 -- how much of everything the job asked for is actually present.
    core = share(required)

    # Areas 2 and 3 -- the same sum, restricted to the two buckets that carry
    # their own weight in the rubric.
    sap = share(required & SAP_PLATFORM_SKILLS)
    genai = share(required & GENAI_SKILLS)

    # Area 4 -- projects that name at least one required skill. Free text, so
    # this is a substring check rather than a set intersection.
    relevant = [p for p in projects if any(s.lower() in p.lower() for s in required)]
    project = len(relevant) / len(projects) if projects else 0.0

    # Area 5 -- a keyword tool cannot judge communication, so breadth of proven
    # relevant skills stands in for it: six or more is full marks.
    consulting = min(1.0, covered(required) / 6)

    parts = {
        "core_technical": core,
        "sap_btp_experience": sap,
        "genai_experience": genai,
        "project_relevance": project,
        "consulting_fit": consulting,
    }
    return {area: round(min(1.0, value) * WEIGHTS[area]) for area, value in parts.items()}


def calculate_fit_score(
    matched_skills: Sequence[str],
    missing_skills: Sequence[str],
    required_skills: Sequence[str],
    partially_matched_skills: Sequence[str] = (),
    projects: Sequence[str] = (),
) -> int:
    """Calculate the candidate fit score out of 100 from the matched skill lists."""
    return sum(
        score_breakdown(
            matched_skills,
            missing_skills,
            required_skills,
            partially_matched_skills,
            projects,
        ).values()
    )


def fit_level_for(score: int) -> str:
    """Turn a score into the label used in the report and the routing decision."""
    if score >= STRONG_FIT:
        return "Strong Fit"
    if score >= MEDIUM_FIT:
        return "Medium to Strong Fit"
    return "Weak Fit"


def apply_recommendation_for(score: int) -> str:
    """One-line verdict: should the candidate press Apply today?"""
    if score >= STRONG_FIT:
        return "Apply now"
    if score >= MEDIUM_FIT:
        return "Apply after improving the resume"
    return "Do not apply yet - close the skill gaps first"


# --------------------------------------------------------------------------- #
# Tool 3 -- learning roadmap generator
# --------------------------------------------------------------------------- #

# Canonical skill -> (how long it takes, what to actually do).
LEARNING_RESOURCES: Dict[str, tuple] = {
    "SAP BTP": ("2 weeks", "SAP Learning Journey 'Discovering SAP BTP'; build a trial subaccount with destinations and role collections."),
    "SAP AI Core": ("3 weeks", "SAP Learning 'Artificial Intelligence with SAP BTP'; deploy one model through AI Core and call it from a CAP service."),
    "SAP Generative AI Hub": ("2 weeks", "Use the Generative AI Hub SDK to run prompts and orchestration against a deployed foundation model."),
    "SAP Joule": ("3 weeks", "SAP Joule Studio in Build; create one Joule skill that calls an OData action, then extend it with a custom agent."),
    "SAP CAP": ("3 weeks", "CAP Node.js tutorial end to end: CDS model, service, HANA deployment, Fiori preview."),
    "SAP RAP": ("4 weeks", "ABAP RAP managed scenario on the ABAP trial system, exposed as an OData V4 service."),
    "SAP Integration Suite": ("3 weeks", "Build two iFlows in Cloud Integration: OData polling and an exception subprocess with retry."),
    "SAP Build Process Automation": ("2 weeks", "Automate one approval workflow with forms, decisions and a bot."),
    "SAP Build Apps": ("1 week", "Build one no-code app on a BTP destination and publish it to the Build lobby."),
    "SAP HANA Cloud": ("2 weeks", "Provision a HANA Cloud trial, create an HDI container, and connect it from CAP."),
    "SAP HANA Cloud Vector Engine": ("2 weeks", "Store embeddings in a REAL_VECTOR column and run a similarity search from Python."),
    "SAP S/4HANA": ("3 weeks", "Explore the S/4HANA OData APIs on api.sap.com and call one from a BTP application."),
    "ABAP": ("4 weeks", "openSAP ABAP basics; write and debug one report and one class-based service."),
    "ABAP Cloud": ("3 weeks", "ABAP Cloud rules, released APIs and the clean-core extensibility model."),
    "LangGraph": ("2 weeks", "Rebuild this agent from scratch: state, nodes, conditional edges, checkpointing."),
    "LangChain": ("1 week", "Chains, prompt templates, structured output and tool binding."),
    "RAG": ("2 weeks", "Chunk, embed and index a document set, then measure retrieval quality before generation."),
    "GraphRAG": ("3 weeks", "Build a knowledge graph over the same documents and compare answers against plain RAG."),
    "Agentic AI": ("3 weeks", "Design a multi-agent workflow with routing, tools and a human approval gate."),
    "Prompt Engineering": ("1 week", "Few-shot prompting, structured output schemas, and evaluation of prompt changes."),
    "Vector Database": ("1 week", "Index the same corpus in two stores and compare recall and latency."),
    "Python": ("4 weeks", "Core Python, typing, and virtual environments; write one small package with tests."),
    "SQL": ("2 weeks", "Joins, window functions and query plans on a sample warehouse schema."),
    "Apache Spark": ("4 weeks", "PySpark DataFrame API; run one batch job over a partitioned dataset."),
    "Apache Airflow": ("2 weeks", "Author one DAG with sensors, retries and backfill."),
    "Docker": ("1 week", "Containerise one service and push it to a registry."),
    "Kubernetes": ("3 weeks", "Deployments, services and config maps on a local cluster."),
}

# Skills with no entry above still deserve a plan, so they fall back to this.
DEFAULT_PLAN = ("2 weeks", "Complete one official tutorial, then build a small hands-on demo you can show.")

# How the roadmap is split up. Highest-value skills go first.
PHASES = [("Days 1-30", 2), ("Days 31-60", 2), ("Days 61-90", None)]


def generate_learning_plan(missing_skills: List[str]) -> str:
    """Generate a 30/60/90 day learning roadmap for the missing skills.

    Skills are taken in the order they were reported, so whatever the gap
    analysis considered most damaging is scheduled first.
    """
    skills = normalize_skills(missing_skills)
    if not skills:
        return "No blocking skill gaps. Spend the time deepening the projects already on the resume."

    lines: List[str] = []
    remaining = list(skills)
    for phase, size in PHASES:
        if not remaining:
            break
        batch, remaining = (remaining, []) if size is None else (remaining[:size], remaining[size:])
        lines.append(f"{phase}")
        for skill in batch:
            effort, action = LEARNING_RESOURCES.get(skill, DEFAULT_PLAN)
            lines.append(f"  - {skill} ({effort}): {action}")
        lines.append("")

    lines.append("Proof of work: publish each item as a public repo or a resume bullet point.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# LangChain tool objects -- for the ToolNode / tools_condition challenge
# --------------------------------------------------------------------------- #
MATCH_TOOLS = [
    as_tool(normalize_skill),
    as_tool(calculate_fit_score),
    as_tool(generate_learning_plan),
]
