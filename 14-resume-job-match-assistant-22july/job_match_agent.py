"""Resume-to-Job Match Assistant -- an agentic workflow on LangGraph + Google Gemini.

Graph
-----
    START -> input_validator
                  |
       missing ---+--- complete
          |             |
          |       resume_parser -> jd_parser -> skill_matching -> gap_analysis
          |                                                            |
          |                                                       fit_score
          |                                                            |
          |          score >= 80 ------------ 60-79 ------------ below 60
          |               |                     |                     |
          |        cover_letter      resume_improvement      learning_roadmap
          |               |                     |                     |
          +---------------+----- final_recommendation ----------------+
                                        |
                                       END

Concepts each part demonstrates:

* ``JobMatchState``          -- shared state passed between nodes, with a reducer on
                                ``history`` so several jobs on one thread accumulate.
* ``*_node`` functions       -- one node = one job, returns only the keys it changes.
* ``route_*``                -- conditional edges that pick the next node from state.
* ``match_tools``            -- deterministic tools the nodes call for scoring.
* ``build_agent(memory=)``   -- checkpointing, so a thread_id remembers past roles.
"""

from __future__ import annotations

import operator
import os
from typing import Annotated, List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from match_tools import apply_recommendation_for, calculate_fit_score, fit_level_for
from match_tools import generate_learning_plan, normalize_skills, score_breakdown
from match_tools import MEDIUM_FIT, STRONG_FIT

load_dotenv()

# Overridable so the project keeps working as new Gemini versions ship.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")


# --------------------------------------------------------------------------- #
# State
# --------------------------------------------------------------------------- #
class JobMatchState(TypedDict, total=False):
    """Shared memory every node reads from and writes to.

    A node returns a partial dict; LangGraph merges it into the state. Plain keys
    are overwritten, but ``history`` carries the ``operator.add`` reducer, so its
    lists are concatenated instead -- that is what lets one thread build up a
    record of every job the candidate has been screened against.
    """

    # inputs
    resume_text: str
    job_description: str
    # agent 1
    resume_available: bool
    jd_available: bool
    missing_information: List[str]
    # agents 2 and 3
    parsed_resume: Optional[dict]
    parsed_jd: Optional[dict]
    # agent 4
    matched_skills: List[str]
    partially_matched_skills: List[str]
    missing_skills: List[str]
    # agents 5 and 6
    gap_analysis: Optional[str]
    fit_score: Optional[int]
    fit_level: Optional[str]
    apply_recommendation: Optional[str]
    score_breakdown: Optional[dict]
    # the three branches
    cover_letter: Optional[str]
    resume_improvement_suggestions: Optional[str]
    learning_roadmap: Optional[str]
    # the closing node
    final_recommendation: Optional[str]
    history: Annotated[List[str], operator.add]


# --------------------------------------------------------------------------- #
# Gemini
# --------------------------------------------------------------------------- #
_llm = None


def get_llm():
    """Build the Gemini client once and reuse it across nodes."""
    global _llm
    if _llm is None:
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Copy .env.example to .env and paste your "
                "key from https://aistudio.google.com/apikey"
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        _llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    return _llm


class ParsedResume(BaseModel):
    """Structured output for the resume parser node."""

    candidate_name: str = Field(description="Candidate name, or 'Not stated'.")
    total_experience: str = Field(description="Total experience, e.g. '6 years'.")
    core_skills: List[str] = Field(description="Technical skills named in the resume.")
    projects: List[str] = Field(description="One short line per project.")
    certifications: List[str] = Field(description="Certifications, empty list if none.")


class ParsedJD(BaseModel):
    """Structured output for the job description parser node."""

    job_title: str = Field(description="The role being advertised.")
    required_skills: List[str] = Field(description="Skills the advert treats as mandatory.")
    preferred_skills: List[str] = Field(description="Skills listed as nice to have.")
    experience_required: str = Field(description="Experience asked for, e.g. '6+ years'.")


class SkillMatch(BaseModel):
    """Structured output for the skill matching node."""

    matched_skills: List[str] = Field(description="Required skills clearly evidenced.")
    partially_matched_skills: List[str] = Field(
        description="Skills with adjacent or indirect evidence only."
    )
    missing_skills: List[str] = Field(description="Required skills with no evidence at all.")


RESUME_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical recruiter reading a resume. Extract only what the "
            "resume actually says. Never invent a skill, a project or a "
            "certification. If the name or experience is not stated, say 'Not stated'.",
        ),
        ("human", "Resume:\n{resume_text}"),
    ]
)

JD_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical recruiter reading a job description. Separate the "
            "mandatory skills from the nice-to-have ones. List each skill as a short "
            "noun phrase such as 'SAP AI Core', not a full sentence.",
        ),
        ("human", "Job description:\n{job_description}"),
    ]
)

MATCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are comparing a candidate against a role. Put every required skill "
            "into exactly one of three lists:\n\n"
            "matched            -- the resume shows direct, hands-on evidence.\n"
            "partially_matched  -- the evidence is adjacent or implied, for example "
            "the candidate used SAP Generative AI Hub but never names Joule.\n"
            "missing            -- nothing in the resume supports it.\n\n"
            "Use the exact skill names from the required list. Do not add skills the "
            "job never asked for, and do not put the same skill in two lists.",
        ),
        (
            "human",
            "Required skills:\n{required_skills}\n\n"
            "Preferred skills:\n{preferred_skills}\n\n"
            "Candidate skills:\n{candidate_skills}\n\n"
            "Candidate projects:\n{projects}",
        ),
    ]
)

GAP_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a career coach. In 4-6 sentences explain how serious the gaps "
            "are: which missing skills would actually block the candidate, which are "
            "cosmetic, and which are probably experience the resume simply fails to "
            "spell out. Be direct and specific. No bullet points, no headings.",
        ),
        (
            "human",
            "Role: {job_title}\n"
            "Matched: {matched_skills}\n"
            "Partially matched: {partially_matched_skills}\n"
            "Missing: {missing_skills}\n"
            "Candidate projects: {projects}",
        ),
    ]
)

COVER_LETTER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the candidate writing to a recruiter. Write a message of at most "
            "150 words: why the role fits, two concrete pieces of evidence from the "
            "projects, and a closing line offering a conversation. Plain text, no "
            "placeholders like [Your Name], no flattery, no invented experience.",
        ),
        (
            "human",
            "Role: {job_title}\n"
            "Candidate: {candidate_name}, {total_experience}\n"
            "Matched skills: {matched_skills}\n"
            "Projects: {projects}",
        ),
    ]
)

IMPROVEMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a resume editor. Give 4-6 numbered edits that would raise this "
            "candidate's score for this specific role. Each edit names the section to "
            "change and the wording to add. Suggest only wording the candidate's own "
            "projects already justify -- never invent experience. Finish with one "
            "rewritten project bullet the candidate can paste in.",
        ),
        (
            "human",
            "Role: {job_title}\n"
            "Fit score: {fit_score}/100\n"
            "Matched: {matched_skills}\n"
            "Partially matched: {partially_matched_skills}\n"
            "Missing: {missing_skills}\n"
            "Projects: {projects}",
        ),
    ]
)

FINAL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a career advisor closing the review. Write the recommendation in "
            "exactly this format, with no extra commentary:\n\n"
            "Verdict: <one sentence: apply, apply after edits, or build skills first>\n"
            "Why: <two sentences grounded in the score and the gaps>\n"
            "Next Step: <one concrete action to take this week>",
        ),
        (
            "human",
            "Role: {job_title}\n"
            "Fit score: {fit_score}/100 ({fit_level})\n"
            "Recommendation band: {apply_recommendation}\n"
            "Matched: {matched_skills}\n"
            "Missing: {missing_skills}\n"
            "Gap analysis: {gap_analysis}",
        ),
    ]
)


def _parse_resume_with_llm(resume_text: str) -> dict:
    """Ask Gemini for the structured resume. Split out so tests can stub the LLM."""
    chain = RESUME_PROMPT | get_llm().with_structured_output(ParsedResume)
    return chain.invoke({"resume_text": resume_text}).model_dump()


def _parse_jd_with_llm(job_description: str) -> dict:
    """Ask Gemini for the structured job description."""
    chain = JD_PROMPT | get_llm().with_structured_output(ParsedJD)
    return chain.invoke({"job_description": job_description}).model_dump()


def _match_with_llm(resume: dict, jd: dict) -> SkillMatch:
    """Ask Gemini to sort the required skills into matched / partial / missing."""
    chain = MATCH_PROMPT | get_llm().with_structured_output(SkillMatch)
    return chain.invoke(
        {
            # Normalised first, so the model is not asked to spot that CPI and
            # Integration Suite are the same product.
            "required_skills": ", ".join(normalize_skills(jd["required_skills"])),
            "preferred_skills": ", ".join(normalize_skills(jd["preferred_skills"])),
            "candidate_skills": ", ".join(normalize_skills(resume["core_skills"])),
            "projects": "; ".join(resume["projects"]) or "none listed",
        }
    )


def _text_of(message) -> str:
    """Pull the plain text out of a chat message.

    ``content`` is not always a string. Gemini 2.5 answers with a list of content
    blocks -- ``[{"type": "reasoning", ...}, {"type": "text", "text": "..."}]`` --
    and calling ``.strip()`` on that list is an AttributeError. Blocks without a
    ``text`` key are the model's own reasoning and are dropped on purpose; only
    what it actually said belongs in the report.
    """
    content = message.content
    if isinstance(content, str):
        return content.strip()
    parts = [
        block if isinstance(block, str) else block.get("text", "")
        for block in content
    ]
    return "".join(parts).strip()


def _write_with_llm(prompt: ChatPromptTemplate, **values) -> str:
    """Run one of the prose prompts and return the text."""
    return _text_of((prompt | get_llm()).invoke(values))


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def input_validator_node(state: JobMatchState) -> dict:
    """Agent 1 -- confirm both inputs arrived before any token is spent.

    A resume of three words is not a resume, so length is checked as well as
    presence; that is what stops the parser hallucinating a candidate out of a
    stray line of text.
    """
    resume = (state.get("resume_text") or "").strip()
    jd = (state.get("job_description") or "").strip()

    missing = []
    if len(resume) < 30:
        missing.append("resume_text")
    if len(jd) < 30:
        missing.append("job_description")

    return {
        "resume_available": "resume_text" not in missing,
        "jd_available": "job_description" not in missing,
        "missing_information": missing,
    }


def resume_parser_node(state: JobMatchState) -> dict:
    """Agent 2 -- pull name, experience, skills, projects and certifications out."""
    return {"parsed_resume": _parse_resume_with_llm(state["resume_text"])}


def jd_parser_node(state: JobMatchState) -> dict:
    """Agent 3 -- pull the title, required and preferred skills out of the advert."""
    parsed = _parse_jd_with_llm(state["job_description"])
    # The reducer on history appends, so a remembered thread ends up holding
    # every role the candidate has been screened against.
    return {"parsed_jd": parsed, "history": [parsed["job_title"]]}


def skill_matching_node(state: JobMatchState) -> dict:
    """Agent 4 -- sort the required skills into matched, partial and missing."""
    match = _match_with_llm(state["parsed_resume"], state["parsed_jd"])
    # Normalised on the way out as well: the model echoes back whatever spelling
    # it likes, and the score tool compares against the taxonomy.
    return {
        "matched_skills": normalize_skills(match.matched_skills),
        "partially_matched_skills": normalize_skills(match.partially_matched_skills),
        "missing_skills": normalize_skills(match.missing_skills),
    }


def gap_analysis_node(state: JobMatchState) -> dict:
    """Agent 5 -- explain which gaps really matter and which are presentation."""
    return {
        "gap_analysis": _write_with_llm(
            GAP_PROMPT,
            job_title=state["parsed_jd"]["job_title"],
            matched_skills=", ".join(state["matched_skills"]) or "none",
            partially_matched_skills=", ".join(state["partially_matched_skills"]) or "none",
            missing_skills=", ".join(state["missing_skills"]) or "none",
            projects="; ".join(state["parsed_resume"]["projects"]) or "none listed",
        )
    }


def fit_score_node(state: JobMatchState) -> dict:
    """Agent 6 -- the score comes from the tool, not the model.

    Arithmetic here rather than a prompt is the whole point: the same inputs
    always produce the same number, and the breakdown says where it came from.
    """
    breakdown = score_breakdown(
        matched_skills=state["matched_skills"],
        missing_skills=state["missing_skills"],
        required_skills=state["parsed_jd"]["required_skills"],
        partially_matched_skills=state["partially_matched_skills"],
        projects=state["parsed_resume"]["projects"],
    )
    score = sum(breakdown.values())
    return {
        "fit_score": score,
        "fit_level": fit_level_for(score),
        "apply_recommendation": apply_recommendation_for(score),
        "score_breakdown": breakdown,
    }


def cover_letter_node(state: JobMatchState) -> dict:
    """Strong-fit branch -- write the recruiter message."""
    resume = state["parsed_resume"]
    return {
        "cover_letter": _write_with_llm(
            COVER_LETTER_PROMPT,
            job_title=state["parsed_jd"]["job_title"],
            candidate_name=resume["candidate_name"],
            total_experience=resume["total_experience"],
            matched_skills=", ".join(state["matched_skills"]),
            projects="; ".join(resume["projects"]) or "none listed",
        )
    }


def resume_improvement_node(state: JobMatchState) -> dict:
    """Medium-fit branch -- the skills are there, the resume hides them."""
    return {
        "resume_improvement_suggestions": _write_with_llm(
            IMPROVEMENT_PROMPT,
            job_title=state["parsed_jd"]["job_title"],
            fit_score=state["fit_score"],
            matched_skills=", ".join(state["matched_skills"]) or "none",
            partially_matched_skills=", ".join(state["partially_matched_skills"]) or "none",
            missing_skills=", ".join(state["missing_skills"]) or "none",
            projects="; ".join(state["parsed_resume"]["projects"]) or "none listed",
        )
    }


def learning_roadmap_node(state: JobMatchState) -> dict:
    """Weak-fit branch -- a real gap, so the tool schedules the study plan."""
    return {"learning_roadmap": generate_learning_plan(state["missing_skills"])}


def final_recommendation_node(state: JobMatchState) -> dict:
    """The closing node every branch feeds into.

    Also the landing point for a failed validation, which is why it answers
    without calling the LLM when the inputs never arrived.
    """
    if state.get("missing_information"):
        missing = ", ".join(state["missing_information"])
        return {
            "final_recommendation": (
                f"Cannot screen this application. Missing or too short: {missing}. "
                "Provide the full text of both the resume and the job description."
            )
        }

    return {
        "final_recommendation": _write_with_llm(
            FINAL_PROMPT,
            job_title=state["parsed_jd"]["job_title"],
            fit_score=state["fit_score"],
            fit_level=state["fit_level"],
            apply_recommendation=state["apply_recommendation"],
            matched_skills=", ".join(state["matched_skills"]) or "none",
            missing_skills=", ".join(state["missing_skills"]) or "none",
            gap_analysis=state["gap_analysis"],
        )
    }


# --------------------------------------------------------------------------- #
# Conditional routing
# --------------------------------------------------------------------------- #
def route_after_validation(state: JobMatchState) -> str:
    """A validator that cannot stop the run is decoration -- so this one stops it."""
    return "final_recommendation" if state["missing_information"] else "resume_parser"


def route_based_on_fit_score(state: JobMatchState) -> str:
    """The decision router from section 5 of the problem statement.

    Strong fit -> sell the candidate. Medium fit -> fix the resume. Weak fit ->
    fix the candidate. Kept apart from ``fit_score_node`` so it can be tested
    without an API key.
    """
    score = state["fit_score"]
    if score >= STRONG_FIT:
        return "cover_letter"
    if score >= MEDIUM_FIT:
        return "resume_improvement"
    return "learning_roadmap"


# --------------------------------------------------------------------------- #
# Graph
# --------------------------------------------------------------------------- #
def build_agent(memory: bool = False):
    """Wire the nodes and edges together and compile the graph.

    ``memory=True`` attaches an InMemorySaver, so invoking with the same
    ``thread_id`` resumes the stored state instead of starting from scratch --
    which is how the same resume accumulates a history of roles it was screened
    against.
    """
    workflow = StateGraph(JobMatchState)

    workflow.add_node("input_validator", input_validator_node)
    workflow.add_node("resume_parser", resume_parser_node)
    workflow.add_node("jd_parser", jd_parser_node)
    workflow.add_node("skill_matching", skill_matching_node)
    workflow.add_node("gap_analysis", gap_analysis_node)
    workflow.add_node("fit_score", fit_score_node)
    workflow.add_node("cover_letter", cover_letter_node)
    workflow.add_node("resume_improvement", resume_improvement_node)
    workflow.add_node("learning_roadmap", learning_roadmap_node)
    workflow.add_node("final_recommendation", final_recommendation_node)

    workflow.add_edge(START, "input_validator")
    workflow.add_conditional_edges(
        "input_validator",
        route_after_validation,
        {"resume_parser": "resume_parser", "final_recommendation": "final_recommendation"},
    )
    workflow.add_edge("resume_parser", "jd_parser")
    workflow.add_edge("jd_parser", "skill_matching")
    workflow.add_edge("skill_matching", "gap_analysis")
    workflow.add_edge("gap_analysis", "fit_score")
    workflow.add_conditional_edges(
        "fit_score",
        route_based_on_fit_score,
        {
            "cover_letter": "cover_letter",
            "resume_improvement": "resume_improvement",
            "learning_roadmap": "learning_roadmap",
        },
    )
    workflow.add_edge("cover_letter", "final_recommendation")
    workflow.add_edge("resume_improvement", "final_recommendation")
    workflow.add_edge("learning_roadmap", "final_recommendation")
    workflow.add_edge("final_recommendation", END)

    return workflow.compile(checkpointer=InMemorySaver() if memory else None)


def run_agent(
    resume_text: str,
    job_description: str,
    app=None,
    thread_id: Optional[str] = None,
) -> JobMatchState:
    """Screen one resume against one job description and return the final state.

    Pass ``thread_id`` together with an ``app`` built by ``build_agent(memory=True)``
    to keep several roles on one remembered thread.
    """
    app = app or build_agent(memory=thread_id is not None)
    config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
    return app.invoke(
        {"resume_text": resume_text, "job_description": job_description},
        config=config,
    )


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def branch_taken(state: JobMatchState) -> str:
    """Which of the three routed nodes actually ran."""
    if state.get("cover_letter"):
        return "cover_letter"
    if state.get("resume_improvement_suggestions"):
        return "resume_improvement"
    if state.get("learning_roadmap"):
        return "learning_roadmap"
    return "none (validation failed)"


def format_report(state: JobMatchState) -> str:
    """Render the run as the Candidate Fit Report from section 9."""
    if state.get("missing_information"):
        return state["final_recommendation"]

    resume, jd = state["parsed_resume"], state["parsed_jd"]
    lines = [
        "Candidate Fit Report",
        "=" * 78,
        f"Candidate  : {resume['candidate_name']} ({resume['total_experience']})",
        f"Role       : {jd['job_title']} (asks for {jd['experience_required']})",
        f"Fit Score  : {state['fit_score']}/100",
        f"Fit Level  : {state['fit_level']}",
        f"Verdict    : {state['apply_recommendation']}",
        "",
        "Score breakdown:",
    ]
    for area, points in state["score_breakdown"].items():
        lines.append(f"  {area.replace('_', ' ').title():<22} {points}")

    lines += [
        "",
        f"Matched Skills          : {', '.join(state['matched_skills']) or 'none'}",
        f"Partially Matched       : {', '.join(state['partially_matched_skills']) or 'none'}",
        f"Missing Skills          : {', '.join(state['missing_skills']) or 'none'}",
        "",
        "Gap Analysis:",
        state["gap_analysis"],
        "",
    ]

    if state.get("cover_letter"):
        lines += ["Recruiter Message:", state["cover_letter"], ""]
    if state.get("resume_improvement_suggestions"):
        lines += ["Suggested Resume Improvements:", state["resume_improvement_suggestions"], ""]
    if state.get("learning_roadmap"):
        lines += ["Learning Roadmap:", state["learning_roadmap"], ""]

    lines += ["Final Recommendation:", state["final_recommendation"]]
    return "\n".join(lines)


def print_graph() -> None:
    """Print the compiled graph as Mermaid -- paste it into any Markdown viewer."""
    print(build_agent().get_graph().draw_mermaid())
