# Problem Statement 14 — Agentic Resume-to-Job Match Assistant (LangGraph)

| | |
|---|---|
| **Project Title** | Agentic AI Resume Screening Assistant using LangGraph and Google Gemini |
| **Domain** | HR Tech / Career Advisory |
| **Topic** | Agentic decision-making — multi-node workflow, conditional routing on a computed score |
| **Stack** | Python · LangGraph · LangChain · Google Gemini (`gemini-2.5-flash`) |
| **Implementation** | [`resume-job-match-assistant-22july/`](../resume-job-match-assistant-22july/) |

---

## Problem Statement

Build an Agentic AI Resume Screening Assistant using LangGraph and Google Gemini.

The system takes two inputs:

1. Candidate resume text
2. Job description text

The agent should behave like an intelligent career advisor. It must **not** produce the final answer in one shot. Instead it follows a multi-step agentic workflow, and a **decision router** chooses what to produce based on how well the candidate scores.

> This exercise teaches **agentic decision-making**, not chatbot development.

## 1. Business Scenario

A candidate wants to apply for SAP BTP + Generative AI / Joule / AI Core roles. They have a resume and a job description. The agent should decide:

- Whether the candidate is a good fit.
- Which skills match.
- Which skills are missing.
- How to improve the resume.
- Whether the candidate should apply.
- What to send the recruiter.

## 2. Agent Workflow

```
START
  |
Input Validator Agent
  |
Resume Parser Agent
  |
Job Description Parser Agent
  |
Skill Matching Agent
  |
Gap Analysis Agent
  |
Fit Score Agent
  |
Decision Router
   |-- Strong fit  -> Cover Letter Generator
   |-- Medium fit  -> Resume Improvement Agent
   |-- Weak fit    -> Learning Roadmap Agent
  |
Final Career Recommendation
  |
END
```

## 3. Agent Responsibilities

### Agent 1 — Input Validator

Checks whether the resume and job description are available.

```json
{
  "resume_available": true,
  "jd_available": true,
  "missing_information": []
}
```

### Agent 2 — Resume Parser

```json
{
  "candidate_name": "Prem Pratik",
  "total_experience": "6 years",
  "core_skills": ["SAP BTP", "Python", "LangGraph", "SAP AI Core"],
  "projects": ["SAP GenAI Hub project", "GraphRAG project"],
  "certifications": ["SAP Business AI Certification"]
}
```

### Agent 3 — Job Description Parser

```json
{
  "job_title": "SAP BTP AI Consultant",
  "required_skills": ["SAP BTP", "SAP AI Core", "Joule", "CAP", "Integration Suite"],
  "preferred_skills": ["LangChain", "LangGraph", "Vector DB", "HANA Cloud"],
  "experience_required": "6+ years"
}
```

### Agent 4 — Skill Matching

```json
{
  "matched_skills": ["SAP BTP", "SAP AI Core", "Python"],
  "partially_matched_skills": ["Joule", "SAP Generative AI Hub"],
  "missing_skills": ["SAP Build Apps", "SAP Workflow Management"]
}
```

### Agent 5 — Gap Analysis

Explains the missing skills and how serious they are. For example:

> The candidate has strong SAP BTP and GenAI exposure, but Joule Studio hands-on experience is not clearly visible in the resume. This should be highlighted if the candidate has worked on SAP Business AI scenarios.

### Agent 6 — Fit Score

Calculates a score out of 100.

| Area | Weight |
|---|---|
| Core technical match | 40 |
| SAP BTP experience | 20 |
| GenAI / Agentic AI experience | 20 |
| Project relevance | 10 |
| Communication / consulting fit | 10 |

```json
{
  "fit_score": 78,
  "fit_level": "Medium to Strong Fit",
  "apply_recommendation": "Apply after improving resume"
}
```

## 4. Conditional Routing

```python
def route_based_on_fit_score(state):
    score = state["fit_score"]
    if score >= 80:
        return "cover_letter_generator"
    elif score >= 60:
        return "resume_improvement_agent"
    else:
        return "learning_roadmap_agent"
```

## 5. Tools to Build

```python
def normalize_skill(skill: str) -> str:
    """
    Normalize similar skill names.
    Example:
    SAP Gen AI -> SAP Generative AI
    BTP        -> SAP BTP
    CPI        -> SAP Integration Suite
    """

def calculate_fit_score(matched_skills: list, missing_skills: list,
                        required_skills: list) -> int:
    """Calculate candidate fit score based on matched and missing skills."""

def generate_learning_plan(missing_skills: list) -> str:
    """Generate a learning roadmap for the missing skills."""
```

## 6. State Design

```python
from typing import TypedDict, List, Optional

class JobMatchState(TypedDict):
    resume_text: str
    job_description: str
    parsed_resume: Optional[dict]
    parsed_jd: Optional[dict]
    matched_skills: List[str]
    partially_matched_skills: List[str]
    missing_skills: List[str]
    gap_analysis: Optional[str]
    fit_score: Optional[int]
    fit_level: Optional[str]
    resume_improvement_suggestions: Optional[str]
    learning_roadmap: Optional[str]
    cover_letter: Optional[str]
    final_recommendation: Optional[str]
```

## 7. Sample Input

**Resume text**

> I have experience in SAP BTP, SAP HANA Cloud, Python, LangChain, LangGraph, RAG, GraphRAG, SAP AI Core, SAP Generative AI Hub, CAP applications, and SAP Build Process Automation. I have built AI agents for SAP support automation and code evaluation.

**Job description**

> We are hiring an SAP BTP AI Consultant with experience in SAP BTP, SAP AI Core, Joule, SAP Generative AI Hub, CAP, Integration Suite, HANA Cloud, and enterprise AI solution architecture. Candidate should understand GenAI, prompt engineering, RAG, and agentic AI workflows.

## 8. Expected Final Output

```
Candidate Fit Report

Fit Score: 85/100
Fit Level: Strong Fit

Matched Skills:
- SAP BTP
- SAP AI Core
- SAP Generative AI Hub
- CAP
- HANA Cloud
- LangGraph
- RAG
- Agentic AI

Missing / Weak Skills:
- Joule Studio hands-on experience is not clearly mentioned
- Integration Suite experience should be highlighted more clearly

Recommendation:
The candidate should apply for this role. The resume should be slightly improved by
adding SAP Joule, SAP Business AI, Integration Suite, and enterprise AI architecture
keywords.

Suggested Resume Improvement:
Add a project section showing how SAP BTP, AI Core, GenAI Hub, and LangGraph were used to
build an enterprise AI solution.

Recruiter Message:
Hi, I am interested in the SAP BTP AI Consultant role. I have hands-on experience in SAP
BTP, SAP AI Core, Generative AI Hub, LangGraph, RAG, GraphRAG, and agentic AI solution
design. I would be happy to discuss how my experience aligns with this role.
```

## 9. Hands-on Tasks

| Task | What to do |
|---|---|
| 1 | `!pip install -q langgraph langchain langchain-google-genai` |
| 2 | Configure Gemini with `ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)` |
| 3 | Create `JobMatchState` |
| 4 | Create the ten nodes: `input_validator`, `resume_parser`, `jd_parser`, `skill_matching`, `gap_analysis`, `fit_score`, `resume_improvement`, `cover_letter`, `learning_roadmap`, `final_recommendation` |
| 5 | Add the conditional routing on the fit score |
| 6 | Compile the graph with `StateGraph(JobMatchState)` |
| 7 | Test the same resume against three job descriptions and compare the scores |

Test the same resume against: **SAP BTP AI Consultant**, **Data Engineer**, and **SAP ABAP Developer**. The three should route down three different branches.

## 10. Evaluation Criteria

| Requirement | Done |
|---|---|
| Uses LangGraph `StateGraph` | [ ] |
| Uses Google Gemini | [ ] |
| Has at least 7 nodes | [ ] |
| Uses conditional routing | [ ] |
| Uses at least 2 tools | [ ] |
| Parses the resume | [ ] |
| Parses the job description | [ ] |
| Matches skills | [ ] |
| Calculates a fit score | [ ] |
| Generates a final recommendation | [ ] |
| Generates a recruiter message or roadmap | [ ] |

## 11. Advanced Extension

- **Human in the loop** — ask the user before generating the recruiter message.
- **Memory** — save previous job descriptions and compare roles.
- **Multi-agent design** — Resume Agent, JD Agent, Skill Match Agent, Career Coach Agent, Recruiter Message Agent.
- **Real-world integration** — upload a PDF resume, extract the text, paste a live job advert, and generate customised resume bullet points.
- **SAP-specific version** — add an SAP skill taxonomy: SAP BTP, CAP, RAP, ABAP Cloud, SAP AI Core, SAP Generative AI Hub, Joule, SAP Integration Suite, SAP Build Process Automation, SAP HANA Cloud Vector Engine.
