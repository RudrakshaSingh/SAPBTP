"""Check the graph wiring without spending a Gemini call.

The two LLM-backed decisions and the drafting step are replaced with stubs, so
this asserts what the graph itself is responsible for: that a High priority
routes through ``ticket``, that Medium/Low skips it, and that only escalated
issues reach ``human_review``.

Run:
    python test_routing.py
"""

from __future__ import annotations

import support_agent
from support_agent import build_agent, run_agent, set_approver

# issue keyword -> (category, priority) the stubbed "LLM" returns.
STUB_TRIAGE = {
    "401": ("SAP Integration Suite / CPI", "High"),
    "destination": ("SAP BTP", "Low"),
    "cap application": ("SAP HANA Cloud", "Medium"),
    "order creation": ("SAP S/4HANA", "High"),
}


def _triage(issue: str):
    lowered = issue.lower()
    for key, value in STUB_TRIAGE.items():
        if key in lowered:
            return value
    return ("General SAP", "Low")


def install_stubs() -> None:
    support_agent._classify_with_llm = lambda issue: _triage(issue)[0]
    support_agent._prioritise_with_llm = lambda issue: _triage(issue)[1]
    support_agent._draft_with_llm = lambda state: (
        f"Issue Category: {state['category']}\n"
        f"Priority: {state['priority']}\n"
        f"Likely Cause: stubbed\n"
        f"Suggested Resolution:\n1. {state['kb_result'].splitlines()[0]}\n"
        f"Escalation Required: {'Yes' if state['needs_human_review'] else 'No'}"
    )
    set_approver(lambda state: True)


CASES = [
    # issue, category, priority, ticket expected, review expected
    ("SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 "
     "unauthorized error. Employee replication has stopped.",
     "SAP Integration Suite / CPI", "High", True, True),
    ("How can I create a destination in SAP BTP cockpit?",
     "SAP BTP", "Low", False, False),
    ("SAP HANA Cloud connection is failing from CAP application.",
     "SAP HANA Cloud", "Medium", False, False),
    ("Production S/4HANA order creation API is down and sales users cannot create orders.",
     "SAP S/4HANA", "High", True, True),
]


def test_routing() -> None:
    install_stubs()
    app = build_agent()
    for issue, category, priority, wants_ticket, wants_review in CASES:
        state = run_agent(issue, app=app)
        assert state["category"] == category, state["category"]
        assert state["priority"] == priority, state["priority"]
        assert bool(state.get("ticket_id")) is wants_ticket, state.get("ticket_id")
        assert state["needs_human_review"] is wants_review
        assert state["final_response"], "no final response produced"
        assert state["kb_result"] and state["system_status"]
        print(f"ok  {priority:<6} ticket={wants_ticket!s:<5} review={wants_review!s:<5} {issue[:46]}...")


def test_rejected_review_blocks_the_response() -> None:
    install_stubs()
    set_approver(lambda state: False)
    state = run_agent(CASES[0][0], app=build_agent())
    assert state["final_response"].startswith("Response rejected")
    print("ok  a rejected review replaces the draft with a revision request")


def test_memory_accumulates_history() -> None:
    install_stubs()
    app = build_agent(memory=True)
    run_agent(CASES[1][0], app=app, thread_id="t1")
    state = run_agent(CASES[2][0], app=app, thread_id="t1")
    assert len(state["history"]) == 2, state["history"]
    run_agent(CASES[3][0], app=app, thread_id="t2")
    print("ok  history accumulates per thread_id")


if __name__ == "__main__":
    test_routing()
    test_rejected_review_blocks_the_response()
    test_memory_accumulates_history()
    print("\nAll graph checks passed.")
