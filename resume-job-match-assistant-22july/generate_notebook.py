"""Build the Colab notebook from the real source files.

The notebook is generated rather than hand-written so its code can never drift
away from match_tools.py / job_match_agent.py -- the modules stay the single
source of truth, and the notebook is a rendered view of them, laid out as the
eight hands-on tasks.

Run:
    python generate_notebook.py
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

NOTEBOOK = Path("Resume_Job_Match_Agent_Colab.ipynb")

BANNER = re.compile(r"^# -{20,} #\n# (.+?)\n# -{20,} #\n", re.MULTILINE)

# Lines that only make sense in the package layout, not in one flat notebook.
DROP_LINES = re.compile(
    r"^(from match_tools import .*|from dotenv import load_dotenv|load_dotenv\(\))$",
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


def clean(body: str) -> str:
    """Remove cross-module imports and the __main__ guard."""
    body = DROP_LINES.sub("", body)
    body = body.split('if __name__ == "__main__":')[0]
    return body.strip("\n")


@lru_cache(maxsize=None)
def sections(module: str) -> dict:
    """Split a module into {banner title: body}.

    Everything before the first banner is filed under 'Setup'. Slicing modules by
    banner is what lets the notebook present them in task order instead of file
    order -- the tools land in Task 4 even though the agent's state is Task 3.
    """
    source = strip_docstring(Path(f"{module}.py").read_text(encoding="utf-8"))
    parts = BANNER.split(source)
    found = {"Setup": parts[0]}
    for i in range(1, len(parts), 2):
        found[parts[i]] = parts[i + 1]
    return found


def code_for(module: str, *titles: str) -> list[dict]:
    """One code cell per named section of a module, in the order given."""
    cells = []
    for title in titles:
        body = clean(sections(module)[title])
        if body:
            cells.append(code(body))
    return cells


INTRO = """
# Resume-to-Job Match Assistant -- LangGraph + Google Gemini

An agentic career advisor. A resume and a job description go in; a fit score, a gap
analysis and either a recruiter message, a resume rewrite or a learning roadmap come out.

The agent never answers in one shot. Eight agents each do one job, and a **decision router**
picks which of the three closing agents runs, based on a score that was calculated in
Python rather than guessed by the model.

```
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
```

Concepts demonstrated: **state** with a reducer, **10 nodes**, **2 conditional edges**,
**3 deterministic tools**, **structured output**, and **checkpointed memory**.

### How the tasks map to the handout

| Notebook | Handout | What you build |
| --- | --- | --- |
| Task 1 | Task 1 | Install the libraries |
| Task 2 | Task 2 | Configure Gemini |
| Task 3 | Task 3 | `JobMatchState` |
| Task 4 | Section 6 | The three tools -- they must exist before the nodes call them |
| Task 5 | Task 4 | The ten nodes |
| Task 6 | Task 5 | Conditional routing |
| Task 7 | Task 6 | Compile the graph |
| Task 8 | Task 7 | Test against three job descriptions |
"""

TASK_1 = """
## Task 1 -- Install the libraries

`langgraph` builds the graph, `langchain-google-genai` talks to Gemini. The `-q` keeps
Colab's output short.
"""

INSTALL = """
!pip install -q langgraph langchain langchain-google-genai
"""

TASK_2 = """
## Task 2 -- Configure Gemini

A local `.env` file is tried first, so restarting the kernel does not mean retyping the key.
In Colab there is no `.env`, so it falls through to `getpass` -- which keeps the key off the
screen, and out of the notebook when you share it.

In VS Code the `getpass` box opens at the **top-centre of the window**, like the command
palette. Clicking anywhere else dismisses it and the cell waits forever, so watch for it.

The model itself is built further down in `get_llm()`, lazily -- so every cell up to Task 7
runs whether or not the key is valid, and only the actual screening needs the network.
"""

KEY = """
import os
from getpass import getpass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google AI Studio API key: ")

print("key loaded:", bool(os.getenv("GOOGLE_API_KEY")))
"""

TASK_3 = """
## Task 3 -- The state

`JobMatchState` is the shared memory. Every node receives it and returns **only the keys it
changed**; LangGraph merges the result in.

Plain keys are overwritten. `history` is different -- the `operator.add` annotation makes it
a *reducer*, so lists are concatenated instead of replaced. That one annotation is the whole
difference between an agent that forgets the last job and one that can compare roles.

Note that `total=False` lets nodes return partial dicts without the type checker objecting.
"""

TASK_4 = """
## Task 4 -- The three tools

A tool here is just a Python function. These three deliberately keep work *away* from the
LLM:

1. **`normalize_skill`** -- the JD says `CPI`, the resume says `SAP Integration Suite`. Without
   normalisation that is a false gap, and the candidate loses points for a skill they have.
2. **`calculate_fit_score`** -- weighted arithmetic, not a prompt. Same inputs, same number,
   every run, and `score_breakdown` shows exactly where the points came from.
3. **`generate_learning_plan`** -- a curated 30/60/90 day schedule, so the roadmap cites real
   SAP learning journeys instead of invented course names.

The taxonomy below is the SAP-specific part of section 12 in the handout.
"""

TAXONOMY_NOTE = """
### The skill taxonomy

`SKILL_SYNONYMS` maps every spelling onto one canonical name, and the last line folds the
canonical names back in as keys so `SAP BTP` normalises to itself.

`SAP_PLATFORM_SKILLS` and `GENAI_SKILLS` are the two buckets the scoring rubric weights
separately -- 20 points each.
"""

TOOL_1_NOTE = """
### Tool 1 -- `normalize_skill`

Punctuation is stripped before the lookup, so `SAP AI Core,` and `(CPI)` and `Node.js` all
reach the same key. An unknown skill is returned unchanged: the taxonomy is a helper, not a
whitelist, so a job asking for Terraform still works.
"""

TOOL_2_NOTE = """
### Tool 2 -- `calculate_fit_score`

The rubric from section 6 of the handout: 40 points for overall coverage, 20 for the SAP
stack, 20 for GenAI, 10 for project relevance, 10 for consulting fit.

Two decisions worth arguing with:

* A partial match earns **half** a point. Change `PARTIAL_CREDIT` and watch the routing
  flip between branches.
* The SAP and GenAI buckets score **zero** when the job asks for nothing from them. That is
  deliberate -- it is why this same resume scores far lower against a Data Engineer advert.
"""

TOOL_3_NOTE = """
### Tool 3 -- `generate_learning_plan`

Skills stay in the order the gap analysis reported them, so whatever was judged most damaging
gets scheduled in the first 30 days. Anything outside `LEARNING_RESOURCES` still gets a plan
via `DEFAULT_PLAN`.
"""

TOOLS_EXPORT_NOTE = """
### The same tools, as LangChain tool objects

The nodes call these functions directly, so the graph does not need them wrapped. This export
exists for the advanced challenge, where Gemini decides which tool to call and `ToolNode`
executes it.
"""

TASK_5 = """
## Task 5 -- The ten nodes

One node, one job. No node calls another -- they only read and write state, which is why the
three branch nodes could be added without touching the six that come before them.

First the Gemini plumbing: `with_structured_output` binds a Pydantic schema to the model, so
the resume and JD come back as validated objects rather than prose to parse. That is what
makes `parsed_jd["required_skills"]` safe to index into two nodes later.

The `_*_with_llm` helpers are separated from the nodes on purpose: it means the routing can
be tested with the LLM stubbed out.
"""

NODES_NOTE = """
### The nodes themselves

Read `fit_score_node` closely -- it is the one node that calls a tool instead of the model.
Everything downstream, including which branch runs, depends on a number the LLM never saw.
"""

TASK_6 = """
## Task 6 -- Conditional routing

A router is a function that reads state and returns the **name of the next node**. Keeping it
separate from the node that produced the decision is what makes it independently testable.

There are two here. `route_after_validation` is the more important one in practice: a
validator that cannot stop the run is decoration.
"""

TASK_7 = """
## Task 7 -- Compile the graph

Ten nodes, two conditional edges, three branches converging back on one closing node.

`build_agent(memory=True)` attaches an `InMemorySaver`, after which invoking with the same
`thread_id` resumes the stored state instead of starting fresh.
"""

GRAPH_IMAGE_NOTE = """
### The compiled graph

Rendered from the graph object itself, so the picture cannot go stale.
"""

GRAPH_IMAGE = """
try:
    from IPython.display import Image, display

    display(Image(build_agent().get_graph().draw_mermaid_png()))
except Exception:
    print(build_agent().get_graph().draw_mermaid())
"""

TASK_8 = """
## Task 8 -- Test against three job descriptions

One resume, three adverts. The resume never changes, so every difference in the score is
produced by the job description alone.

Expect the SAP BTP AI role to score highest, and the two non-SAP roles to fall into the
weak-fit branch. The exact numbers depend on how Gemini sorts the skills, so treat them as a
target rather than a guarantee -- a score you disagree with is a prompt to sharpen
`MATCH_PROMPT` or the weights in `WEIGHTS`.
"""

DEMO = """
app = build_agent()

results = []
for label, jd in JOB_DESCRIPTIONS:
    print("=" * 78)
    print(f"Screening against: {label}")
    print("=" * 78)
    state = run_agent(SAMPLE_RESUME, jd, app=app)
    print(format_report(state))
    print()
    results.append((label, state))

print("=" * 78)
print("Same resume, three roles")
print("=" * 78)
print(f"{'Role':<26}{'Score':<8}{'Fit Level':<24}Branch taken")
print("-" * 78)
for label, state in results:
    print(f"{label:<26}{str(state['fit_score']) + '/100':<8}"
          f"{state['fit_level']:<24}{branch_taken(state)}")
"""

MEMORY_NOTE = """
## Task 9 (extension) -- Memory

Three roles, one `thread_id`. The checkpointer restores the stored state before each run, and
the `operator.add` reducer on `history` keeps every job title -- which is the "save previous
job descriptions and compare roles" extension from section 12.
"""

MEMORY = """
remembering = build_agent(memory=True)

for _, jd in JOB_DESCRIPTIONS:
    state = run_agent(SAMPLE_RESUME, jd, app=remembering, thread_id="candidate-prem")
    print(f"  {state['parsed_jd']['job_title']:<26}{state['fit_score']}/100")

print("\\nRoles screened on thread candidate-prem:")
for n, role in enumerate(state["history"], start=1):
    print(f"  {n}. {role}")
"""

VALIDATOR_NOTE = """
## Task 10 (extension) -- Prove the validator branch

The happy path never touches `route_after_validation`. Send in an empty job description and
the graph should skip all six analysis nodes and land straight on `final_recommendation` --
no API call, no hallucinated candidate.
"""

VALIDATOR_DEMO = """
state = run_agent(SAMPLE_RESUME, "", app=app)

print("Missing information :", state["missing_information"])
print("Branch taken        :", branch_taken(state))
print("Parsed resume       :", state.get("parsed_resume"))
print()
print(format_report(state))
"""

OUTRO = """
## Where to take it next

- **Human in the loop** -- pause before the recruiter message and ask for approval, using
  LangGraph's `interrupt()` so the graph resumes from the checkpoint.
- **Real resumes** -- read a PDF with `pypdf` and feed the extracted text to `run_agent`.
- **Score the preferred skills too** -- they are parsed but currently only inform the match.
- **Tool calling** -- let Gemini pick the tools with `ToolNode` + `tools_condition` instead of
  fixed nodes; `MATCH_TOOLS` already exports them as LangChain tools.
- **Loop back** -- feed the resume improvements into a second screening run and check whether
  the score actually moves. That is the closest thing to a self-improving agent here.
"""


def main() -> None:
    cells = [
        md(INTRO),
        md(TASK_1),
        code(INSTALL),
        md(TASK_2),
        code(KEY),
        md(TASK_3),
        *code_for("job_match_agent", "Setup", "State"),
        md(TASK_4),
        md(TAXONOMY_NOTE),
        *code_for("match_tools", "Setup", "SAP + GenAI skill taxonomy"),
        md(TOOL_1_NOTE),
        *code_for("match_tools", "Tool 1 -- skill normalizer"),
        md(TOOL_2_NOTE),
        *code_for("match_tools", "Tool 2 -- fit score calculator"),
        md(TOOL_3_NOTE),
        *code_for("match_tools", "Tool 3 -- learning roadmap generator"),
        md(TOOLS_EXPORT_NOTE),
        *code_for("match_tools", "LangChain tool objects -- for the ToolNode / tools_condition challenge"),
        md(TASK_5),
        *code_for("job_match_agent", "Gemini"),
        md(NODES_NOTE),
        *code_for("job_match_agent", "Nodes"),
        md(TASK_6),
        *code_for("job_match_agent", "Conditional routing"),
        md(TASK_7),
        *code_for("job_match_agent", "Graph", "Reporting"),
        md(GRAPH_IMAGE_NOTE),
        code(GRAPH_IMAGE),
        md(TASK_8),
        *code_for("sample_data", "Setup"),
        code(DEMO),
        md(MEMORY_NOTE),
        code(MEMORY),
        md(VALIDATOR_NOTE),
        code(VALIDATOR_DEMO),
        md(OUTRO),
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
