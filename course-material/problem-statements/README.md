# Problem Statements

Structured markdown version of the course hands-on problem statements — one file per problem.

| # | Problem Statement | Domain | Topic | File |
|---|---|---|---|---|
| 1 | Student Training Academy DBMS | EdTech | RDBMS with SQLite + Python + Pandas | [01-student-training-academy-dbms.md](01-student-training-academy-dbms.md) |
| 2 | Revenue by Course Report | EdTech | SQL — joins, conditional aggregation | [02-revenue-by-course-report.md](02-revenue-by-course-report.md) |
| 3 | Student Payment Summary View | EdTech | SQL — views, CASE categorization | [03-student-payment-summary-view.md](03-student-payment-summary-view.md) |
| 4 | HR Employee Management System | Human Resources | RDBMS — keys, constraints, relationships | [04-hr-employee-management-rdbms.md](04-hr-employee-management-rdbms.md) |
| 5 | Hospital OPD Appointment & Billing Analytics | Healthcare | SQL — schema design, views, analytics | [05-hospital-opd-appointment-billing-analytics.md](05-hospital-opd-appointment-billing-analytics.md) |
| 6 | Retail Sales Analysis using Pandas and SQL | Retail | SQL + Pandas | [06-retail-sales-analysis-pandas-sql.md](06-retail-sales-analysis-pandas-sql.md) |
| 7 | Employee Salary Prediction | HR Analytics | ML — Regression | [07-employee-salary-prediction-regression.md](07-employee-salary-prediction-regression.md) |
| 8 | Loan Default Risk Prediction | Fintech | ML — Binary Classification | [08-loan-default-risk-classification.md](08-loan-default-risk-classification.md) |
| 9 | House Rent Prediction | Real Estate | Deep Learning — ANN Regression | [09-house-rent-prediction-ann.md](09-house-rent-prediction-ann.md) |
| 10 | SmartKart Customer Support Assistant | E-commerce | LangChain + Gemini, tool calling | [10-langchain-gemini-customer-support-assistant.md](10-langchain-gemini-customer-support-assistant.md) |
| 11 | Course Recommendation Assistant | EdTech | RAG — FAISS, Pydantic structured output | [11-course-recommendation-rag-assistant.md](11-course-recommendation-rag-assistant.md) |
| 12 | SAP Incident Knowledge Assistant | SAP Operations | RAG over structured Excel data | [12-sap-incident-knowledge-assistant-rag.md](12-sap-incident-knowledge-assistant-rag.md) |
| 13 | SAP Support Agent | SAP Operations | Agentic AI — LangGraph StateGraph | [13-sap-support-agent-langgraph.md](13-sap-support-agent-langgraph.md) |
| 14 | Resume-to-Job Match Assistant | HR Tech | Agentic AI — LangGraph, conditional routing | [14-resume-job-match-agent-langgraph.md](14-resume-job-match-agent-langgraph.md) |

## Learning Progression

```
RDBMS foundation + Python  →  1
SQL reporting & views      →  2, 3, 4, 5
Data analysis (SQL+Pandas) →  6
Classical ML               →  7 (regression), 8 (classification)
Deep Learning              →  9 (ANN regression)
LLM apps & tool calling    →  10
RAG                        →  11 (documents), 12 (structured Excel data)
Agentic AI (LangGraph)     →  13 (support routing), 14 (decision routing)
```

## Implementation Folders

Problems 10–14 have a working implementation in this repository:

| # | Problem | Implementation |
|---|---|---|
| 10 | SmartKart Customer Support Assistant | [`smartkart-support-assistant-14july/`](../smartkart-support-assistant-14july/) |
| 11 | Course Recommendation Assistant | [`course-recommendation-assistant 15 july/`](../course-recommendation-assistant%2015%20july/) |
| 12 | SAP Incident Knowledge Assistant | [`sap-incident-knowledge-assistant16july/`](../sap-incident-knowledge-assistant16july/) |
| 13 | SAP Support Agent | [`sap-support-agent-langgraph21july/`](../sap-support-agent-langgraph21july/) |
| 14 | Resume-to-Job Match Assistant | [`resume-job-match-assistant-22july/`](../resume-job-match-assistant-22july/) |

## Sources

| Problems | Source document |
|---|---|
| 1 | `course-material/Tasks.docx` |
| 2 – 10 | `All Problem Statements upto 15th July.pdf` (96 pages) |
| 12, 13, 14 | `PROBLEM_STATEMENT.md` in each project folder |
| 11 | Derived from the project's `README.md` and source code (no problem statement doc existed) |

## Notes

- The PDF numbers its problems 1–9; here they are shifted to **2–10** so the Tasks.docx hands-on sits first. Problem 6 in this folder is the one labelled **"5a"** in the PDF (there is no "5b" in the source).
- Problem 10 and the `smartkart-support-assistant-14july/` folder are the **same assignment** — the folder is the implementation, so it is not listed as a separate problem.
- Numeric tables in problems 7, 8, and 9 (model comparison tables) are **illustrative expected values** from the source document, not results you must reproduce exactly.
