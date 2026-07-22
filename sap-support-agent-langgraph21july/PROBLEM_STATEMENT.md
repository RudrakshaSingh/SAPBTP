# Hands-on Exercise: Build an SAP Support Agent using LangGraph

## Problem Statement

You need to build an Agentic AI assistant for an SAP support team. The agent should
receive a user issue, understand the problem, decide whether it needs a tool, search a
small knowledge base, classify priority, and generate a final support response.

This exercise teaches LangGraph concepts like state, nodes, edges, conditional routing,
tool calling, and memory/checkpointing. LangGraph's Graph API is built around
`StateGraph`, where nodes are Python functions and conditional edges route execution
based on state. For Gemini, use LangChain's `ChatGoogleGenerativeAI` integration through
the `langchain-google-genai` package.

## 1. Business Scenario

A company uses SAP BTP, SAP Integration Suite, SuccessFactors, S/4HANA, and SAP HANA
Cloud. Users raise support issues like:

> Our SuccessFactors employee replication to S/4HANA is failing through CPI.
> The error says 401 unauthorized in the OData call.

Your LangGraph agent should:

1. Understand the issue.
2. Classify the SAP area.
3. Decide whether to search a knowledge base.
4. Use tools when needed.
5. Decide priority.
6. Generate a final support response.
7. Escalate to human review if priority is high.

## 2. Concepts Covered

| Concept | What you will build |
| --- | --- |
| State | Shared memory passed between graph nodes |
| Node | Python function performing one task |
| Edge | Flow from one node to another |
| Conditional edge | Dynamic routing based on state |
| Tool | Python function callable by the agent |
| Agentic workflow | LLM decides next action |
| Memory | Keep conversation/thread state |
| Human-in-loop | Simulated human approval step |

LangGraph also provides prebuilt tool patterns like `ToolNode` and `tools_condition` for
routing between an LLM node and tools.

## 3. Final Goal

Input:

```
My SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 unauthorized error.
Employee data is not getting replicated.
```

Expected output:

```
Issue Category: SAP Integration Suite / CPI
Priority: High
Likely Cause: Authentication failure in OData destination or expired credentials.
Suggested Resolution:
1. Check SAP BTP destination credentials.
2. Validate OAuth/client credential configuration.
3. Test the OData endpoint directly.
4. Review CPI message monitoring logs.
5. Reprocess the failed iFlow after credential correction.
Escalation Required: Yes
```

## 4. Tools to Create

```python
def search_kb(query: str) -> str:
    """Search SAP support knowledge base. Return relevant troubleshooting steps."""

def check_system_status(system_name: str) -> str:
    """Return mock system status. Example: CPI = Running, S4HANA = Degraded."""

def create_support_ticket(summary: str, priority: str) -> str:
    """Create a mock support ticket and return ticket ID."""
```

## 5. State Design

```python
from typing import TypedDict, List, Optional

class SupportAgentState(TypedDict):
    user_issue: str
    category: Optional[str]
    priority: Optional[str]
    kb_result: Optional[str]
    system_status: Optional[str]
    draft_response: Optional[str]
    final_response: Optional[str]
    ticket_id: Optional[str]
    needs_human_review: bool
```

## 6. Graph Nodes

1. **Intake** -- store and clean the user issue.
2. **Classification** -- Gemini picks one of: SAP BTP, SAP Integration Suite / CPI,
   SAP SuccessFactors, SAP S/4HANA, SAP HANA Cloud, SAP Build Process Automation,
   General SAP.
3. **Priority** -- production down / replication stopped / payment issue = High,
   single user issue = Medium, general question = Low. High also sets
   `needs_human_review`.
4. **Knowledge base tool** -- call `search_kb()`.
5. **System status** -- call `check_system_status()` for the systems involved.
6. **Draft response** -- Gemini writes Issue Category, Priority, Likely Cause,
   Troubleshooting Steps, Escalation Required.
7. **Human review** -- simulate approval; a rejection asks for a revision.
8. **Ticket creation** -- `create_support_ticket()` on the High branch.

## 7. Conditional Routing Logic

```python
def route_after_priority(state):
    return "ticket" if state["priority"] == "High" else "kb_search"

def route_after_draft(state):
    return "human_review" if state["needs_human_review"] else "final"
```

## 8. Graph Flow

```
START
  v
intake
  v
classify_issue
  v
assign_priority
  v
conditional route:
    High priority -> create_ticket -> kb_search
    Medium/Low    -> kb_search
  v
check_system_status
  v
draft_response
  v
conditional route:
    needs human review -> human_review -> END
    no review          -> final -> END
```

## 9. Starter Code Structure

```python
!pip install -q langgraph langchain langchain-google-genai

import os
from getpass import getpass
os.environ["GOOGLE_API_KEY"] = getpass("Enter your Google AI Studio API key: ")

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

from langgraph.graph import StateGraph, START, END
workflow = StateGraph(SupportAgentState)
# ... add_node / add_edge / add_conditional_edges ...
app = workflow.compile()
```

## 10. Test Cases

| # | Issue | Category | Priority | Ticket | Review |
| --- | --- | --- | --- | --- | --- |
| 1 | SAP CPI integration from SuccessFactors to S/4HANA is failing with 401 unauthorized error. Employee replication has stopped. | SAP Integration Suite / CPI | High | Yes | Yes |
| 2 | How can I create a destination in SAP BTP cockpit? | SAP BTP | Low | No | No |
| 3 | SAP HANA Cloud connection is failing from CAP application. | SAP HANA Cloud / SAP BTP | Medium | No | No |
| 4 | Production S/4HANA order creation API is down and sales users cannot create orders. | SAP S/4HANA | High | Yes | Yes |

## 11. Evaluation Criteria

| Requirement | Done |
| --- | --- |
| Uses Google Gemini as LLM | [ ] |
| Uses LangGraph StateGraph | [ ] |
| Has at least 6 nodes | [ ] |
| Has at least 2 conditional edges | [ ] |
| Uses at least 2 tools | [ ] |
| Classifies issue category | [ ] |
| Assigns priority | [ ] |
| Searches mock KB | [ ] |
| Creates ticket for high priority | [ ] |
| Simulates human approval | [ ] |
| Produces final structured response | [ ] |

## 12. Advanced Challenge

- **Memory** -- store previous issues using LangGraph checkpointing (`InMemorySaver`) and
  ask follow-up questions using previous context.
- **Tool calling agent** -- replace manual tool nodes with Gemini tool calling, using
  `ToolNode` and `tools_condition`.
- **Multi-agent design** -- issue classifier, SAP technical resolver, escalation manager,
  final response writer.
- **Real-world SAP extension** -- connect to the Jira API, store issue logs in SAP HANA
  Cloud, and swap Gemini for SAP AI Core / Generative AI Hub.

## 13. Mini Assignment Submission Format

1. Problem solved
2. Graph diagram
3. State schema
4. Node descriptions
5. Tool descriptions
6. Code
7. Test case outputs
8. What you learned
9. Improvements possible
