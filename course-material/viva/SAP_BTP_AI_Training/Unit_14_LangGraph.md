# 🌐 Unit 14 — LangGraph

> **Module**: Module 5 — Agentic AI  
> **Duration**: Day 25–26 (16 hours)  
> **Dates**: 31-Jul-2026, 03-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — What is LangGraph?

### Q1. What is LangGraph? Why was it created?

**A:** **LangGraph** is a framework built on top of LangChain for building **stateful, multi-actor applications** using a graph-based architecture.

**Why it was created:**
- Traditional LangChain chains are **stateless** and **linear** (A → B → C → end).
- Real-world agents need **cycles** (loop back), **branching** (if/else), and **state** (persist context across steps).
- LangGraph brings **graphs** (nodes + edges) instead of chains, enabling:
  - **Cycles** — Loop until task is done or max iterations reached.
  - **Branching** — Conditional routing based on state.
  - **State management** — Shared, typed state persisted across all nodes.
  - **Human-in-the-loop** — Pause the graph, wait for approval, then resume.
  - **Persistence** — Save graph state to resume after interruption.

---

### Q2. What are the core concepts in LangGraph?

**A:**

| Concept | Definition | Example |
|---------|-----------|---------|
| **State** | A shared TypedDict passed between all nodes | `{"messages": [...], "documents": [...], "answer": ""}` |
| **Node** | A function that receives state, does work, and returns updated state | `retrieve_docs`, `generate_answer`, `check_quality` |
| **Edge** | Connection between nodes; defines the flow | `"retrieve" → "generate"` |
| **Conditional Edge** | Route to different nodes based on state | If answer quality good → END, else → regenerate |
| **Graph** | The complete workflow (StateGraph) | All nodes + edges assembled |
| **Checkpointer** | Saves state for persistence/HITL | `MemorySaver`, `SqliteSaver` |
| **Entrypoint** | The first node to run | `graph.set_entry_point("retrieve")` |
| **END** | Special node that signals graph completion | `graph.add_edge("generate", END)` |

---

### Q3. How does LangGraph differ from LangChain LCEL?

**A:**

| Aspect | LangChain LCEL | LangGraph |
|--------|---------------|-----------|
| **Structure** | Linear pipelines | Directed graphs (nodes + edges) |
| **Cycles** | ❌ No (must use loops explicitly) | ✅ Yes (native graph cycles) |
| **State** | Input/output passed through chain | Shared typed state across all nodes |
| **Branching** | Limited | Full conditional routing |
| **HITL** | Complex to add | Built-in with interrupt/resume |
| **Persistence** | None | Built-in checkpointing |
| **Multi-agent** | Possible but complex | First-class support |
| **Best for** | Simple linear pipelines, RAG | Complex agents, multi-actor systems |

---

## 🔹 Section 2 — Building with LangGraph

### Q4. What is the State in LangGraph?

**A:** **State** is the central shared data structure passed between all nodes. Every node reads from and writes to this state.

```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

# Simple state
class SimpleState(TypedDict):
    question: str
    context: list[str]
    answer: str
    iteration: int

# State with message list (for conversation agents)
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    # Annotated with operator.add → new messages are APPENDED, not replaced
    documents: list[str]
    answer: str
```

**`Annotated[list, operator.add]`** is LangGraph's way of saying: "When multiple nodes update this field, add/merge the values instead of replacing."

---

### Q5. How do you build a simple LangGraph workflow?

**A:**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 1. Define State
class RAGState(TypedDict):
    question: str
    documents: list[str]
    answer: str

# 2. Define Nodes (functions that update state)
def retrieve(state: RAGState) -> dict:
    """Retrieve relevant documents."""
    docs = vector_store.similarity_search(state["question"], k=3)
    return {"documents": [d.page_content for d in docs]}

def generate(state: RAGState) -> dict:
    """Generate answer from retrieved documents."""
    context = "\n\n".join(state["documents"])
    prompt = f"Answer using only this context:\n{context}\n\nQuestion: {state['question']}"
    answer = llm.invoke(prompt).content
    return {"answer": answer}

# 3. Build Graph
builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)

# 4. Add Edges
builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

# 5. Compile
graph = builder.compile()

# 6. Run
result = graph.invoke({"question": "How many annual leaves?", "documents": [], "answer": ""})
print(result["answer"])
```

---

### Q6. How do conditional edges work in LangGraph?

**A:** **Conditional edges** route to different nodes based on the current state.

```python
from langgraph.graph import StateGraph, END

def check_answer_quality(state: RAGState) -> str:
    """Returns the name of the next node to execute."""
    if not state["answer"]:
        return "generate"                        # No answer yet → generate
    elif "not found" in state["answer"].lower():
        return "web_search"                      # Fallback to web search
    elif state["iteration"] >= 3:
        return "end"                             # Max iterations → stop
    else:
        return "grade_answer"                   # Have answer → grade it

# Add conditional edge:
builder.add_conditional_edges(
    "generate",                                  # From this node
    check_answer_quality,                        # Call this function to decide
    {
        "generate": "generate",                  # If returns "generate" → go to generate
        "web_search": "web_search",             # If returns "web_search" → go there
        "grade_answer": "grade_answer",         # If returns "grade_answer" → go there
        "end": END                               # If returns "end" → terminate
    }
)
```

---

### Q7. Build a complete Corrective RAG (CRAG) workflow with LangGraph.

**A:**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class CRAGState(TypedDict):
    question: str
    documents: list
    relevant_docs: list
    answer: str

def retrieve(state):
    docs = retriever.invoke(state["question"])
    return {"documents": docs}

def grade_documents(state):
    """Grade each document for relevance."""
    relevant = []
    for doc in state["documents"]:
        grade_prompt = f"Is this document relevant to: '{state['question']}'? Doc: {doc.page_content[:200]}\nAnswer: yes or no"
        result = llm.invoke(grade_prompt).content.strip().lower()
        if "yes" in result:
            relevant.append(doc)
    return {"relevant_docs": relevant}

def decide_to_generate(state) -> str:
    """Route based on document relevance."""
    if not state["relevant_docs"]:
        return "web_search"    # No relevant docs → search web
    return "generate"          # Have relevant docs → generate answer

def web_search(state):
    results = search_tool.invoke(state["question"])
    return {"relevant_docs": [Document(page_content=results)]}

def generate(state):
    context = "\n".join([d.page_content for d in state["relevant_docs"]])
    answer = llm.invoke(f"Answer using context:\n{context}\n\nQ: {state['question']}").content
    return {"answer": answer}

# Build CRAG graph
builder = StateGraph(CRAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("grade_documents", grade_documents)
builder.add_node("web_search", web_search)
builder.add_node("generate", generate)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "grade_documents")
builder.add_conditional_edges("grade_documents", decide_to_generate,
    {"web_search": "web_search", "generate": "generate"})
builder.add_edge("web_search", "generate")
builder.add_edge("generate", END)

crag_graph = builder.compile()
```

---

## 🔹 Section 3 — Advanced LangGraph Features

### Q8. What is Human-in-the-Loop (HITL) in LangGraph?

**A:** LangGraph supports **pausing the graph** at specific points to wait for human input, then **resuming** from where it stopped.

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class AgentState(TypedDict):
    messages: list
    action_to_approve: str
    approved: bool

def plan_action(state):
    action = llm.invoke("What action should I take? " + str(state["messages"])).content
    return {"action_to_approve": action}

def execute_action(state):
    if not state["approved"]:
        return {"messages": state["messages"] + ["Action cancelled by user."]}
    # Execute the approved action
    result = execute(state["action_to_approve"])
    return {"messages": state["messages"] + [result]}

def should_interrupt(state) -> str:
    return "wait_for_human"  # Always interrupt before execution

builder = StateGraph(AgentState)
builder.add_node("plan", plan_action)
builder.add_node("execute", execute_action)
builder.set_entry_point("plan")

# Add interrupt BEFORE execute node
builder.add_conditional_edges("plan", should_interrupt, {"wait_for_human": "execute"})
builder.add_edge("execute", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["execute"])

# Run until interrupt
config = {"configurable": {"thread_id": "session-1"}}
result = graph.invoke({"messages": ["Book a flight to Delhi"], "action_to_approve": "", "approved": False}, config)
# Graph stops before "execute" — shows action_to_approve to user

# User approves:
result = graph.invoke({"approved": True}, config)  # Resume with approval
```

---

### Q9. What is a Checkpointer in LangGraph?

**A:** A **Checkpointer** saves the graph's state after every node execution, enabling:
- **Persistence** — Resume a workflow after a crash or restart.
- **HITL** — Pause and wait for human input.
- **Debugging** — Inspect state at any point in time.
- **Multi-session** — Different users have different thread IDs.

```python
from langgraph.checkpoint.memory import MemorySaver       # In-memory (development)
from langgraph.checkpoint.sqlite import SqliteSaver       # SQLite (simple production)
# from langgraph.checkpoint.postgres import PostgresSaver  # PostgreSQL (production)

# Memory-based (lost on restart)
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# SQLite-based (persists across restarts)
with SqliteSaver.from_conn_string("./state.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)

    # Thread ID groups messages into a conversation
    config = {"configurable": {"thread_id": "user-123-session-1"}}
    result = graph.invoke({"question": "..."}, config)

    # Inspect saved state
    state = graph.get_state(config)
    print(state.values)  # Current state
    print(state.next)    # Next nodes to execute
```

---

### Q10. How do you build a multi-agent system with LangGraph?

**A:**

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

# Create specialized sub-agents
research_agent = create_react_agent(llm, tools=[web_search], name="researcher")
analyst_agent = create_react_agent(llm, tools=[python_repl], name="analyst")
writer_agent = create_react_agent(llm, tools=[], name="writer")

class TeamState(TypedDict):
    messages: Annotated[list, operator.add]
    research: str
    analysis: str
    report: str
    next_agent: str

def route_to_agent(state) -> str:
    return state["next_agent"]

def research_node(state):
    result = research_agent.invoke(state)
    return {"research": result["messages"][-1].content, "next_agent": "analyst"}

def analyst_node(state):
    result = analyst_agent.invoke({"messages": [HumanMessage(content=state["research"])]})
    return {"analysis": result["messages"][-1].content, "next_agent": "writer"}

def writer_node(state):
    combined = f"Research: {state['research']}\nAnalysis: {state['analysis']}"
    result = writer_agent.invoke({"messages": [HumanMessage(content=combined)]})
    return {"report": result["messages"][-1].content, "next_agent": "end"}

builder = StateGraph(TeamState)
builder.add_node("researcher", research_node)
builder.add_node("analyst", analyst_node)
builder.add_node("writer", writer_node)

builder.set_entry_point("researcher")
builder.add_edge("researcher", "analyst")
builder.add_edge("analyst", "writer")
builder.add_edge("writer", END)

team_graph = builder.compile()
```

---

## 🔹 Section 4 — LangGraph Patterns

### Q11. What is the ReAct agent pattern in LangGraph?

**A:**

```python
from langgraph.prebuilt import create_react_agent

# create_react_agent implements this graph automatically:
#
# [START] → [LLM decides: use tool or final answer?]
#                 ↓ tool call
#           [Execute tool]
#                 ↓ observation
#           [LLM receives observation, decides next step]
#           (cycles until LLM says "Final Answer")
#                 ↓
#           [END]

agent = create_react_agent(
    llm,
    tools=[web_search, calculator, python_repl],
    state_modifier="You are a helpful AI assistant. Use tools when needed."
)

result = agent.invoke({"messages": [HumanMessage(content="Calculate 15% of Apple's market cap")]})
```

---

### Q12. What is the Supervisor pattern in LangGraph?

**A:** A **Supervisor** node decides which worker agent to activate next.

```python
class SupervisorState(TypedDict):
    messages: Annotated[list, operator.add]
    next_agent: str

members = ["researcher", "coder", "writer"]

def supervisor(state) -> dict:
    system_prompt = f"""You are a supervisor managing: {members}.
    Based on the conversation, who should act next?
    When the task is complete, respond with 'FINISH'.
    Respond with ONLY the agent name or 'FINISH'."""

    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    next_agent = response.content.strip()
    return {"next_agent": next_agent}

def route_to_agent(state) -> str:
    if state["next_agent"] == "FINISH":
        return END
    return state["next_agent"]

builder = StateGraph(SupervisorState)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher_node)
builder.add_node("coder", coder_node)
builder.add_node("writer", writer_node)

builder.set_entry_point("supervisor")
builder.add_conditional_edges("supervisor", route_to_agent)
for agent in ["researcher", "coder", "writer"]:
    builder.add_edge(agent, "supervisor")  # All agents report back to supervisor
```

---

### Q13. What is `create_react_agent` vs building a graph manually?

**A:**

| Aspect | `create_react_agent` | Manual graph |
|--------|---------------------|-------------|
| Simplicity | Very simple (1 line) | Complex (20+ lines) |
| Flexibility | Limited to ReAct pattern | Fully customizable |
| Debugging | Less transparent | Full control |
| HITL | Limited | Full HITL support |
| Custom state | ❌ Fixed message state | ✅ Any TypedDict |
| Best for | Standard ReAct agents | Complex custom workflows |

Use `create_react_agent` for standard agents. Build manually for custom logic.

---

## 🔹 Section 5 — LangGraph in Production

### Q14. How do you stream LangGraph execution?

**A:**

```python
# Stream events (see every node execution in real-time)
config = {"configurable": {"thread_id": "session-1"}}

for event in graph.stream({"question": "How many leaves?"}, config):
    for node_name, node_output in event.items():
        print(f"\n--- Node: {node_name} ---")
        print(node_output)

# Stream LLM tokens (for chat applications)
for event in graph.astream_events(input_data, config, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="", flush=True)
```

---

### Q15. What is LangGraph's `.get_state()` and `.get_state_history()`?

**A:**

```python
config = {"configurable": {"thread_id": "session-1"}}

# Get current state
state = graph.get_state(config)
print(state.values)          # Current state values
print(state.next)            # Next nodes to execute (if paused)
print(state.created_at)      # Timestamp

# Update state manually (e.g., inject human input)
graph.update_state(config, {"approved": True})

# Get full history of all states
for state in graph.get_state_history(config):
    print(state.values, state.created_at)

# Go back to a previous state (time travel!)
old_config = {"configurable": {"thread_id": "session-1", "checkpoint_id": old_checkpoint_id}}
result = graph.invoke(None, old_config)  # Resume from old state
```

---

## 🔹 Section 6 — Quick Fire Questions

### Q16. What is the difference between `add_edge` and `add_conditional_edges`?

**A:**
- **`add_edge(a, b)`** — Always goes from node `a` to node `b`.
- **`add_conditional_edges(a, fn, mapping)`** — Goes from node `a` to whichever node `fn(state)` returns.

---

### Q17. What is `operator.add` in LangGraph state?

**A:** `Annotated[list[BaseMessage], operator.add]` tells LangGraph to **append** new messages to the list instead of replacing it. Without this annotation, each node's return value would overwrite the entire list.

```python
# Without annotation: Node 2's messages replace Node 1's messages
# With operator.add: Node 1's messages + Node 2's messages are combined
messages: Annotated[list[BaseMessage], operator.add]
```

---

### Q18. What is `interrupt_before` vs `interrupt_after`?

**A:**
- **`interrupt_before=["node_name"]`** — Pause BEFORE the node executes. Use for approval before an action.
- **`interrupt_after=["node_name"]`** — Pause AFTER the node executes. Use to review output before continuing.

---

### Q19. Can LangGraph work without LangChain?

**A:** Yes! LangGraph can work with any LLM or tool implementation. It just provides the graph orchestration. The LangChain dependency is optional — you can bring your own LLM calls. However, using LangChain components (ChatModels, Tools, etc.) integrates most naturally.

---

### Q20. What is LangGraph Cloud / LangGraph Studio?

**A:**
- **LangGraph Studio** — Visual IDE for designing, testing, and debugging LangGraph graphs. Shows the graph visually, lets you step through executions.
- **LangGraph Cloud** — Managed deployment for LangGraph applications. Handles scaling, persistence, and monitoring.

---

> **💡 Viva Tip:** LangGraph is the "advanced" topic. Show you understand WHEN to use it (complex agents with loops, HITL, multi-actor) vs when simpler LCEL chains suffice. The State → Node → Edge pattern is the most important concept to explain clearly.

---

*End of Unit 14 — LangGraph 🌐*
