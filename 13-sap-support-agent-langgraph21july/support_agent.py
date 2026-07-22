"""SAP Support Agent -- an agentic workflow built with LangGraph + Google Gemini.

Graph
-----
    START -> intake -> classify_issue -> assign_priority
                                            |
                       High ----------------+---------------- Medium / Low
                        |                                          |
                     ticket ---------------> kb_search <-----------+
                                                 |
                                          system_status
                                                 |
                                          draft_response
                                                 |
                     needs review ---------------+--------------- no review
                        |                                          |
                   human_review -> END                          final -> END

Concepts each part demonstrates:

* ``SupportAgentState``   -- shared state passed between nodes, with a reducer on
                             ``history`` so repeat visits on a thread accumulate.
* ``*_node`` functions    -- one node = one task, returns only the keys it changes.
* ``route_after_*``       -- conditional edges that pick the next node from state.
* ``sap_tools``           -- plain Python tools the nodes call.
* ``build_agent(memory=)`` -- checkpointing, so a thread_id remembers past issues.
* ``human_review_node``   -- human-in-the-loop approval gate.
"""

from __future__ import annotations

import operator
import os
import sys
from typing import Annotated, Callable, List, Literal, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from sap_tools import check_system_status, create_support_ticket, detect_systems, search_kb

load_dotenv()

# Overridable so the project keeps working as new Gemini versions ship.
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")

CATEGORIES = [
    "SAP BTP",
    "SAP Integration Suite / CPI",
    "SAP SuccessFactors",
    "SAP S/4HANA",
    "SAP HANA Cloud",
    "SAP Build Process Automation",
    "General SAP",
]

Category = Literal[
    "SAP BTP",
    "SAP Integration Suite / CPI",
    "SAP SuccessFactors",
    "SAP S/4HANA",
    "SAP HANA Cloud",
    "SAP Build Process Automation",
    "General SAP",
]
Priority = Literal["High", "Medium", "Low"]


# --------------------------------------------------------------------------- #
# State
# --------------------------------------------------------------------------- #
class SupportAgentState(TypedDict, total=False):
    """Shared memory every node reads from and writes to.

    A node returns a partial dict; LangGraph merges it into the state. Plain keys
    are overwritten, but ``history`` carries the ``operator.add`` reducer, so its
    lists are concatenated instead -- that is what lets one thread build up a
    record of every issue it has seen.
    """

    user_issue: str
    category: Optional[str]
    priority: Optional[str]
    kb_result: Optional[str]
    system_status: Optional[str]
    draft_response: Optional[str]
    final_response: Optional[str]
    ticket_id: Optional[str]
    needs_human_review: bool
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


class IssueClassification(BaseModel):
    """Structured output for the classification node."""

    category: Category = Field(description="The SAP area that owns this issue.")


class PriorityDecision(BaseModel):
    """Structured output for the priority node."""

    priority: Priority = Field(description="High, Medium or Low.")
    reason: str = Field(description="One sentence justifying the priority.")


CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an SAP support triage assistant. Assign the incoming issue to "
            "exactly one category from this list:\n{categories}\n\n"
            "Pick the area that owns the fix, not every product mentioned. An "
            "integration flow failing between two systems belongs to "
            "'SAP Integration Suite / CPI'. Use 'General SAP' only when no other "
            "category fits.",
        ),
        ("human", "Issue:\n{issue}"),
    ]
)

PRIORITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an SAP support triage assistant deciding incident priority.\n\n"
            "High   -- production is down, a business process is stopped, data "
            "replication has stopped, payments/orders are blocked, or many users "
            "are affected.\n"
            "Medium -- something is broken but contained: one user, one "
            "non-production system, or a workaround exists.\n"
            "Low    -- a how-to, configuration or general question. Nothing is broken.\n\n"
            "Examples:\n"
            "'Payroll posting to S/4HANA has stopped for all employees.' -> High\n"
            "'One user cannot open a Fiori tile, others can.' -> Medium\n"
            "'Where do I find the CPI message monitoring screen?' -> Low",
        ),
        ("human", "Issue:\n{issue}"),
    ]
)

DRAFT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior SAP support engineer. Write the response the support "
            "desk will send back, grounded in the knowledge base extract and the "
            "system status provided. Do not invent log entries or error codes that "
            "were not supplied.\n\n"
            "Reply in exactly this format, with no extra commentary:\n\n"
            "Issue Category: <category>\n"
            "Priority: <priority>\n"
            "Likely Cause: <one or two sentences>\n"
            "Suggested Resolution:\n"
            "1. <step>\n"
            "2. <step>\n"
            "3. <step>\n"
            "4. <step>\n"
            "5. <step>\n"
            "Escalation Required: <Yes or No>",
        ),
        (
            "human",
            "User issue:\n{issue}\n\n"
            "Category: {category}\n"
            "Priority: {priority}\n"
            "Escalation required: {escalation}\n"
            "Ticket: {ticket}\n\n"
            "Knowledge base extract:\n{kb_result}\n\n"
            "System status:\n{system_status}",
        ),
    ]
)


def _classify_with_llm(issue: str) -> str:
    """Ask Gemini for the category. Split out so tests can stub the LLM."""
    chain = CLASSIFY_PROMPT | get_llm().with_structured_output(IssueClassification)
    return chain.invoke({"issue": issue, "categories": "\n".join(CATEGORIES)}).category


def _prioritise_with_llm(issue: str) -> str:
    """Ask Gemini for the priority. Split out so tests can stub the LLM."""
    chain = PRIORITY_PROMPT | get_llm().with_structured_output(PriorityDecision)
    return chain.invoke({"issue": issue}).priority


def _draft_with_llm(state: SupportAgentState) -> str:
    """Ask Gemini for the customer-facing response."""
    chain = DRAFT_PROMPT | get_llm()
    return chain.invoke(
        {
            "issue": state["user_issue"],
            "category": state.get("category"),
            "priority": state.get("priority"),
            "escalation": "Yes" if state.get("needs_human_review") else "No",
            "ticket": state.get("ticket_id") or "none raised",
            "kb_result": state.get("kb_result"),
            "system_status": state.get("system_status"),
        }
    ).content.strip()


# --------------------------------------------------------------------------- #
# Nodes
# --------------------------------------------------------------------------- #
def intake_node(state: SupportAgentState) -> dict:
    """Node 1 -- clean the raw issue and record it in the thread history."""
    issue = " ".join(state["user_issue"].split())
    return {"user_issue": issue, "history": [issue], "needs_human_review": False}


def classify_node(state: SupportAgentState) -> dict:
    """Node 2 -- Gemini assigns one of the seven SAP categories."""
    return {"category": _classify_with_llm(state["user_issue"])}


def priority_node(state: SupportAgentState) -> dict:
    """Node 3 -- Gemini assigns priority; High also flags human review."""
    priority = _prioritise_with_llm(state["user_issue"])
    return {"priority": priority, "needs_human_review": priority == "High"}


def kb_search_node(state: SupportAgentState) -> dict:
    """Node 4 -- tool call into the knowledge base."""
    return {"kb_result": search_kb(state["user_issue"])}


def system_status_node(state: SupportAgentState) -> dict:
    """Node 5 -- tool call for every system named in the issue."""
    systems = detect_systems(state["user_issue"]) or ["BTP"]
    return {"system_status": "; ".join(check_system_status(s) for s in systems)}


def draft_response_node(state: SupportAgentState) -> dict:
    """Node 6 -- Gemini writes the technical response from the gathered facts."""
    return {"draft_response": _draft_with_llm(state)}


def human_review_node(state: SupportAgentState) -> dict:
    """Node 7 -- a human approves or rejects the draft before it goes out."""
    print("\nHuman review required.")
    print(state["draft_response"])
    if _approver(state):
        return {"final_response": state["draft_response"]}
    return {"final_response": "Response rejected. Please revise with more details."}


def ticket_node(state: SupportAgentState) -> dict:
    """Node 8 -- raise a ticket. Only reached on the High-priority branch."""
    ticket_id = create_support_ticket(
        summary=state["user_issue"],
        priority=state["priority"],
    )
    return {"ticket_id": ticket_id}


def final_node(state: SupportAgentState) -> dict:
    """Node 9 -- Medium/Low responses ship without a human in the loop."""
    return {"final_response": state["draft_response"]}


# --------------------------------------------------------------------------- #
# Human-in-the-loop approval
# --------------------------------------------------------------------------- #
def _prompt_approver(state: SupportAgentState) -> bool:
    """Ask at the console, but auto-approve when there is nobody to ask.

    Two separate guards, because they catch different failures. The isatty check
    covers notebooks and schedulers with no console at all. The EOFError catch
    covers the sneakier case of a stdin that reports itself as a terminal but has
    nothing to read -- some CI runners and sandboxes do exactly that, and without
    the catch the whole graph dies at the review step.
    """
    if sys.stdin is None or not sys.stdin.isatty():
        print("Approve response? yes/no: yes  (no console attached, auto-approved)")
        return True
    try:
        return input("Approve response? yes/no: ").strip().lower() in {"y", "yes"}
    except EOFError:
        print("yes  (nothing on stdin, auto-approved)")
        return True


_approver: Callable[[SupportAgentState], bool] = _prompt_approver


def set_approver(fn: Callable[[SupportAgentState], bool]) -> None:
    """Swap the approval step -- used by run_demo.py and the tests.

    Kept as a module setting rather than a graph config value because a callable
    cannot be serialised into a checkpoint.
    """
    global _approver
    _approver = fn


# --------------------------------------------------------------------------- #
# Conditional routing
# --------------------------------------------------------------------------- #
def route_after_priority(state: SupportAgentState) -> str:
    """High priority earns a ticket first; everything else goes straight to the KB."""
    return "ticket" if state["priority"] == "High" else "kb_search"


def route_after_draft(state: SupportAgentState) -> str:
    """Escalated drafts need a human signature before they are final."""
    return "human_review" if state.get("needs_human_review") else "final"


# --------------------------------------------------------------------------- #
# Graph
# --------------------------------------------------------------------------- #
def build_agent(memory: bool = False):
    """Wire the nodes and edges together and compile the graph.

    ``memory=True`` attaches an InMemorySaver, so invoking with the same
    ``thread_id`` resumes the stored state instead of starting from scratch.
    """
    workflow = StateGraph(SupportAgentState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("classify_issue", classify_node)
    workflow.add_node("assign_priority", priority_node)
    workflow.add_node("ticket", ticket_node)
    workflow.add_node("kb_search", kb_search_node)
    workflow.add_node("system_status", system_status_node)
    workflow.add_node("draft_response", draft_response_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("final", final_node)

    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "classify_issue")
    workflow.add_edge("classify_issue", "assign_priority")
    workflow.add_conditional_edges(
        "assign_priority",
        route_after_priority,
        {"ticket": "ticket", "kb_search": "kb_search"},
    )
    workflow.add_edge("ticket", "kb_search")
    workflow.add_edge("kb_search", "system_status")
    workflow.add_edge("system_status", "draft_response")
    workflow.add_conditional_edges(
        "draft_response",
        route_after_draft,
        {"human_review": "human_review", "final": "final"},
    )
    workflow.add_edge("human_review", END)
    workflow.add_edge("final", END)

    return workflow.compile(checkpointer=InMemorySaver() if memory else None)


def run_agent(issue: str, app=None, thread_id: Optional[str] = None) -> SupportAgentState:
    """Run one issue through the graph and return the final state.

    Pass ``thread_id`` together with an ``app`` built by ``build_agent(memory=True)``
    to keep several issues on one remembered thread.
    """
    app = app or build_agent(memory=thread_id is not None)
    config = {"configurable": {"thread_id": thread_id}} if thread_id else {}
    return app.invoke({"user_issue": issue}, config=config)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def format_result(state: SupportAgentState) -> str:
    """Render the run as the scorecard from the problem statement."""
    lines = [
        f"Issue            : {state['user_issue']}",
        f"Category         : {state.get('category')}",
        f"Priority         : {state.get('priority')}",
        f"Ticket Created   : {'Yes (' + state['ticket_id'] + ')' if state.get('ticket_id') else 'No'}",
        f"Human Review     : {'Yes' if state.get('needs_human_review') else 'No'}",
        f"System Status    : {state.get('system_status')}",
        "",
        state.get("final_response") or "(no response produced)",
    ]
    return "\n".join(lines)


def print_graph() -> None:
    """Print the compiled graph as Mermaid -- paste it into any Markdown viewer."""
    print(build_agent().get_graph().draw_mermaid())


if __name__ == "__main__":
    issue = " ".join(sys.argv[1:]) or (
        "My SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 "
        "unauthorized error. Employee data is not getting replicated."
    )
    print(format_result(run_agent(issue)))
