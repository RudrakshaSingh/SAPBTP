# Resume-to-Job Match Assistant

An agentic career advisor built with **LangGraph** and **Google Gemini**. A resume and a
job description go in; a fit score, a gap analysis, and either a recruiter message, a
resume rewrite or a learning roadmap come out.

The agent never answers in one shot. Ten nodes each do one job, and a **decision router**
picks which of the three closing agents runs — based on a score calculated in Python
rather than guessed by the model.

Full brief: [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md).

## The graph

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

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste your key from https://aistudio.google.com/apikey

python app.py                 # the sample resume against all three job descriptions
python app.py --jd 1          # only the SAP BTP AI Consultant advert
python app.py --memory        # all three roles on one remembered thread
python app.py --graph         # print the compiled graph as Mermaid, no API call

python app.py --resume my_cv.txt --jd-file jd.txt    # your own files
```

Or open [Resume_Job_Match_Agent_Colab.ipynb](Resume_Job_Match_Agent_Colab.ipynb) in Colab
and work through Tasks 1-10.

## Files

| File | What it holds |
| --- | --- |
| [app.py](app.py) | Root entry point — runs the demo, your own files, or prints the graph |
| [job_match_agent.py](job_match_agent.py) | State, prompts, the ten nodes, the two routers, the graph |
| [match_tools.py](match_tools.py) | The three tools plus the SAP + GenAI skill taxonomy |
| [sample_data.py](sample_data.py) | One resume, three job descriptions |
| [generate_notebook.py](generate_notebook.py) | Rebuilds the notebook from the modules above |
| [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md) | The exercise brief |

The notebook is **generated**, not hand-written, so its code cannot drift from the
modules. After editing any module:

```bash
python generate_notebook.py
```

## The three tools, and why they are not prompts

| Tool | Job |
| --- | --- |
| `normalize_skill` | The advert says `CPI`, the resume says `SAP Integration Suite`. Without normalising, that is a false gap and the candidate loses points for a skill they have. |
| `calculate_fit_score` | Weighted arithmetic over the matched/partial/missing lists. Same inputs, same number, every run — and `score_breakdown` shows where each point came from. |
| `generate_learning_plan` | A curated 30/60/90 day schedule, so the roadmap cites real SAP learning journeys instead of invented course names. |

The scoring rubric (section 3 of the brief):

| Area | Weight |
| --- | --- |
| Core technical match | 40 |
| SAP BTP experience | 20 |
| GenAI / Agentic AI experience | 20 |
| Project relevance | 10 |
| Communication / consulting fit | 10 |

Two decisions worth arguing with:

- A partially matched skill earns **half** a point. Change `PARTIAL_CREDIT` in
  [match_tools.py](match_tools.py) and the routing flips between branches.
- The SAP and GenAI buckets score **zero** when the job asks for nothing from them. That
  is deliberate — it is why the same resume scores far lower against the Data Engineer
  advert than the SAP BTP one.

Scores move a little between runs because the *matching* is Gemini's judgement even though
the *arithmetic* is not. A score you disagree with is a prompt to sharpen `MATCH_PROMPT` or
the weights in `WEIGHTS`.

## Evaluation criteria

| Requirement | Where |
| --- | --- |
| Uses LangGraph `StateGraph` | `build_agent()` |
| Uses Google Gemini | `get_llm()`, `gemini-2.5-flash` |
| At least 7 nodes | 10 nodes |
| Conditional routing | `route_after_validation`, `route_based_on_fit_score` |
| At least 2 tools | 3 tools in `match_tools.py` |
| Parses resume / job description | `resume_parser_node`, `jd_parser_node` — Pydantic structured output |
| Matches skills | `skill_matching_node` |
| Calculates fit score | `fit_score_node` |
| Final recommendation | `final_recommendation_node` |
| Recruiter message or roadmap | `cover_letter_node`, `learning_roadmap_node` |
| Memory (extension) | `build_agent(memory=True)` + the `operator.add` reducer on `history` |

## Where to take it next

- **Human in the loop** — pause before the recruiter message using LangGraph's
  `interrupt()`, so the graph resumes from the checkpoint instead of blocking.
- **Real resumes** — read a PDF with `pypdf` and pass the extracted text to `run_agent`.
- **Score the preferred skills too** — they are parsed but currently only inform matching.
- **Tool calling** — let Gemini pick the tools with `ToolNode` + `tools_condition`;
  `MATCH_TOOLS` already exports them as LangChain tools.
- **Loop back** — feed the resume improvements into a second screening run and check
  whether the score actually moves.
