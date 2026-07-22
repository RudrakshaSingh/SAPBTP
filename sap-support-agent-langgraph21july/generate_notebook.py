"""Build the Colab notebook from the real source files.

The notebook is generated rather than hand-written so its code can never drift
away from sap_tools.py / support_agent.py -- the modules stay the single source
of truth, and the notebook is a rendered view of them.

Run:
    python generate_notebook.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

NOTEBOOK = Path("SAP_Support_Agent_LangGraph_Colab.ipynb")

BANNER = re.compile(r"^# -{20,} #\n# (.+?)\n# -{20,} #\n", re.MULTILINE)

# Lines that only make sense in the package layout, not in one flat notebook.
DROP_LINES = re.compile(
    r"^(from sap_tools import .*|from dotenv import load_dotenv|load_dotenv\(\))$",
    re.MULTILINE,
)


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


def clean(body: str) -> str:
    """Remove cross-module imports and the __main__ guard."""
    body = DROP_LINES.sub("", body)
    body = body.split('if __name__ == "__main__":')[0]
    return body.strip("\n")


# Markdown that introduces each section, keyed by banner title.
NOTES = {
    "sap_tools:Setup": """
## Part 1 -- the tools

A tool is just a Python function the agent can call. These three stand in for the
systems a real SAP support desk would query: a knowledge base, a monitoring dashboard,
and a ticketing system.
""",
    "sap_tools:Knowledge base": """
### The knowledge base

`SAP_KB` holds the article text and `KB_KEYWORDS` holds the words that should pull each
article up. Keeping them apart means the documentation stays readable while the matching
logic can get as clever as it needs to.
""",
    "sap_tools:Mock system landscape": """
### The mock landscape

Every status is `Running`. Change one to `Degraded` and re-run the demo -- the drafted
response starts blaming the platform instead of the configuration, which is a quick way
to see how much the LLM is really using the facts it was handed.
""",
    "sap_tools:Tool 1 -- knowledge base search": """
### Tool 1 -- `search_kb`

Scores every article by how many of its trigger words appear, then returns the best
three. Matching is whole-word, not substring -- with plain `in` checks,
*"Production S/4HANA order creation API is down"* also matched the **hana connection**
article, because `"hana" in "s/4hana"` is `True`.
""",
    "sap_tools:Tool 2 -- system status": """
### Tool 2 -- `check_system_status`

Users write `S/4HANA`, `s4 hana` and `ECC` for the same box, so aliases are resolved
before lookup. `detect_systems` reads the issue text and returns every system mentioned,
longest alias first so `s/4hana` is consumed before bare `hana` can match it.
""",
    "sap_tools:Tool 3 -- ticket creation": """
### Tool 3 -- `create_support_ticket`

Returns an ID like `INC-20260721-P1-001`. The print statement is the giveaway that the
High-priority branch actually ran.
""",
    "sap_tools:LangChain tool objects -- for the ToolNode / tools_condition challenge": """
### Tools as LangChain objects

The graph calls these functions directly, so it does not need them wrapped. This export
exists for the advanced challenge, where Gemini decides which tool to call and `ToolNode`
executes it.
""",
    "support_agent:Setup": """
## Part 2 -- the agent

Categories are declared twice: once as a list for the prompt, once as a `Literal` for the
structured output schema. The `Literal` is what stops Gemini returning
*"SAP Integration Suite (CPI)"* and silently breaking a router that compares strings.
""",
    "support_agent:State": """
### State

Every node receives this dict and returns only the keys it changed; LangGraph merges the
result. Plain keys are overwritten -- but `history` carries the `operator.add` reducer, so
its lists are concatenated instead. That one annotation is the whole difference between an
agent that forgets and an agent that accumulates.
""",
    "support_agent:Gemini": """
### Gemini, and the two decisions that drive the graph

`with_structured_output` binds a Pydantic schema to the model, so classification and
prioritisation come back as validated objects rather than prose to parse.

The three `_*_with_llm` helpers are separated from the nodes on purpose: it lets the
routing be tested with the LLM stubbed out, which is what `test_routing.py` does.
""",
    "support_agent:Nodes": """
### Nodes

One node, one job. Note that no node calls another -- they only read and write state,
which is why adding `system_status` to the flow required no change to any other node.
""",
    "support_agent:Human-in-the-loop approval": """
### Human-in-the-loop

`input()` is called only when a console is attached. In Colab there is none, so the review
auto-approves rather than hanging the cell. Use `set_approver` to plug in your own
decision -- a real prompt, an always-reject, or a Slack round-trip.
""",
    "support_agent:Conditional routing": """
### Conditional edges

A router is a function that reads state and returns the *name* of the next node. Keeping
it separate from the node that made the decision is what makes the routing independently
testable.
""",
    "support_agent:Graph": """
### The graph

Nine nodes, two conditional edges. `build_agent(memory=True)` attaches an `InMemorySaver`,
after which invoking with the same `thread_id` resumes the stored state instead of
starting fresh.
""",
    "support_agent:Reporting": """
### Reporting
""",
}

INTRO = """
# SAP Support Agent -- LangGraph + Google Gemini

An agentic support desk for SAP issues. One user complaint goes in; a triaged, grounded,
optionally escalated support response comes out.

```
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
```

Concepts demonstrated: **state** with a reducer, **nodes**, **conditional edges**,
**tools**, **checkpointed memory**, and a **human-in-the-loop** approval gate.
"""

INSTALL = """
!pip install -q langgraph langchain langchain-google-genai
"""

KEY = """
import os
from getpass import getpass

os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google AI Studio API key: ")
"""

DEMO = """
app = build_agent()

TEST_CASES = [
    ("SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 "
     "unauthorized error. Employee replication has stopped.",
     "SAP Integration Suite / CPI | High | ticket | review"),
    ("How can I create a destination in SAP BTP cockpit?",
     "SAP BTP | Low | no ticket | no review"),
    ("SAP HANA Cloud connection is failing from CAP application.",
     "SAP HANA Cloud | Medium | no ticket | no review"),
    ("Production S/4HANA order creation API is down and sales users cannot create orders.",
     "SAP S/4HANA | High | ticket | review"),
]

for i, (issue, expected) in enumerate(TEST_CASES, start=1):
    print("=" * 78)
    print(f"Test Case {i}   expected -> {expected}")
    print("=" * 78)
    print(format_result(run_agent(issue, app=app)))
    print()
"""

MEMORY = """
remembering = build_agent(memory=True)

run_agent(TEST_CASES[0][0], app=remembering, thread_id="ticket-4711")
state = run_agent(
    "The same CPI iFlow is still failing after we rotated the client secret.",
    app=remembering,
    thread_id="ticket-4711",
)

print("Issues seen on thread ticket-4711:")
for n, past in enumerate(state["history"], start=1):
    print(f"  {n}. {past}")
"""

GRAPH_IMAGE = """
try:
    from IPython.display import Image, display

    display(Image(build_agent().get_graph().draw_mermaid_png()))
except Exception:
    print(build_agent().get_graph().draw_mermaid())
"""


def cells_for(module: str) -> list[dict]:
    """One markdown note plus one code cell per banner section of a module."""
    source = strip_docstring(Path(f"{module}.py").read_text(encoding="utf-8"))
    cells: list[dict] = []
    for title, body in split_sections(source):
        body = clean(body)
        if not body:
            continue
        note = NOTES.get(f"{module}:{title}")
        if note:
            cells.append(md(note))
        cells.append(code(body))
    return cells


def main() -> None:
    cells = [
        md(INTRO),
        code(INSTALL),
        md("Paste your key from [Google AI Studio](https://aistudio.google.com/apikey)."),
        code(KEY),
        *cells_for("sap_tools"),
        *cells_for("support_agent"),
        md("### The compiled graph\n\nRendered from the graph object itself, so it cannot go stale."),
        code(GRAPH_IMAGE),
        md("## Part 3 -- the four test cases\n\nCategory and priority come from Gemini, so treat the expected values as the target rather than a guarantee. A disagreement is a prompt to sharpen the rules in `PRIORITY_PROMPT`."),
        code(DEMO),
        md("## Part 4 -- memory\n\nTwo issues, one `thread_id`. The checkpointer restores the stored state before the second run, and the `operator.add` reducer on `history` keeps both."),
        code(MEMORY),
        md("""
## Where to take it next

- Move `ticket` after `draft_response` so the incident includes the suggested fix.
- Route a rejected review back to `draft_response` with the reviewer's comment, making it
  a real revision loop.
- Swap `human_review` for LangGraph's `interrupt()` so the graph pauses and resumes from
  the checkpoint instead of blocking on `input()`.
- Let Gemini pick the tools with `ToolNode` + `tools_condition` instead of fixed nodes.
- Split the workflow into classifier / resolver / escalation / writer agents.
"""),
    ]

    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {"provenance": [], "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }

    NOTEBOOK.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(f"Wrote {NOTEBOOK} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
