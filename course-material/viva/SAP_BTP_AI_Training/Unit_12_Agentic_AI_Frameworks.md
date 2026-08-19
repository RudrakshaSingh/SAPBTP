# 🔧 Unit 12 — Agentic AI Frameworks

> **Module**: Module 5 — Agentic AI  
> **Duration**: Day 22 (8 hours)  
> **Date**: 28-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — Framework Landscape

### Q1. What are agentic AI frameworks? Why use them?

**A:** **Agentic AI frameworks** are libraries that provide pre-built components for building AI agents — handling the complex plumbing of LLM calls, tool management, memory, and orchestration.

**Without a framework you'd need to write:**
- Tool calling and result parsing.
- Retry logic for LLM failures.
- Conversation history management.
- Agent loop logic (when to stop).
- Prompt templates for each agent type.

**Why use frameworks:**
- **Speed** — Build agents in hours instead of days.
- **Best practices** — Framework encodes proven patterns.
- **Reliability** — Tested error handling and edge cases.
- **Ecosystem** — Pre-built tools, integrations, connectors.

---

### Q2. Compare the major agentic AI frameworks.

**A:**

| Framework | Company | Focus | Complexity | Best For |
|-----------|---------|-------|-----------|---------|
| **LangChain** | LangChain Inc. | General-purpose LLM apps + agents | Medium | Most use cases |
| **LangGraph** | LangChain Inc. | Stateful, graph-based agent workflows | Medium-High | Complex multi-step agents |
| **CrewAI** | CrewAI | Multi-agent role-based collaboration | Low-Medium | Multi-agent teams |
| **AutoGen** | Microsoft | Multi-agent conversations | Medium | Research, code generation |
| **Semantic Kernel** | Microsoft | Plugin-based, enterprise | Medium | .NET/enterprise workloads |
| **LlamaIndex** | LlamaIndex | Data + RAG focus | Medium | Data-heavy agents |
| **OpenAI Swarm** | OpenAI | Lightweight handoff-based | Low | Simple multi-agent |
| **SAP AI Core** | SAP | SAP-integrated orchestration | High | SAP enterprise agents |

---

### Q3. What is LangChain's agent architecture?

**A:** LangChain agents follow the **ReAct** pattern using:
1. **LLM** — The reasoning engine.
2. **Tools** — Functions the agent can call.
3. **Agent executor** — Manages the loop (call LLM → parse → call tool → observe → repeat).

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def web_search(query: str) -> str:
    """Search the web for information. Use for current events or facts."""
    return tavily_client.search(query)

@tool
def calculate(expression: str) -> str:
    """Evaluate a math expression. Input must be valid Python math."""
    return str(eval(expression))

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
tools = [web_search, calculate]

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)

result = executor.invoke({"input": "What is 15% of Apple's current market cap?"})
```

---

### Q4. What is CrewAI? How does it differ from LangChain?

**A:** **CrewAI** focuses on **role-based multi-agent collaboration** — defining a "crew" of specialized agents with specific roles and tasks.

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find accurate information about AI trends",
    backstory="Expert analyst with 10 years in tech research",
    tools=[web_search],
    llm=llm
)

writer = Agent(
    role="Content Writer",
    goal="Write clear, engaging blog posts",
    backstory="Experienced writer specializing in tech content",
    llm=llm
)

research_task = Task(
    description="Research top 5 AI trends in 2026",
    agent=researcher
)

writing_task = Task(
    description="Write a 500-word blog post based on the research",
    agent=writer
)

crew = Crew(agents=[researcher, writer], tasks=[research_task, writing_task])
result = crew.kickoff()
```

**LangChain vs CrewAI:**

| Aspect | LangChain | CrewAI |
|--------|----------|--------|
| Focus | General LLM + agent building | Multi-agent collaboration |
| Agent model | ReAct, function calling | Role-based, collaborative |
| Simplicity | More complex | Easier multi-agent setup |
| Flexibility | Very high | More opinionated |

---

### Q5. What is Microsoft AutoGen?

**A:** **AutoGen** enables multi-agent conversations where agents can take on different roles and chat with each other to solve complex problems.

**Key concept — Conversable Agents:**
```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="AI_Assistant",
    llm_config={"model": "gpt-4", "api_key": "..."}
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",  # Fully automated
    code_execution_config={"work_dir": "./code"}
)

# Start a conversation between agents
user_proxy.initiate_chat(
    assistant,
    message="Write and run a Python script to analyze this CSV data"
)
```

**AutoGen strength:** Code execution — the assistant writes code, the user proxy executes it, reports results back, and the cycle continues until the task is done.

---

### Q6. What is Microsoft Semantic Kernel?

**A:** **Semantic Kernel** is Microsoft's AI SDK for building AI applications, primarily for .NET but also available in Python and Java.

**Key concepts:**
- **Plugins:** Collections of functions (native code or LLM prompts) the kernel can use.
- **Planner:** Automatically creates a plan of plugin calls to achieve a goal.
- **Memory:** Semantic memory using embeddings.

```python
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

kernel = Kernel()

class EmailPlugin:
    @kernel_function(description="Send an email to the specified address")
    def send_email(self, to: str, subject: str, body: str) -> str:
        # Send email logic
        return f"Email sent to {to}"

kernel.add_plugin(EmailPlugin(), plugin_name="Email")
# Kernel can now use send_email when planning how to complete a task
```

---

## 🔹 Section 2 — Agentic Design Patterns

### Q7. What are the key agentic design patterns?

**A:**

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **ReAct** | Reason → Act → Observe loop | General-purpose agent tasks |
| **Plan-and-Execute** | Create full plan first, then execute | Complex, multi-step tasks |
| **Reflexion** | Agent reflects and improves its own output | Quality-sensitive tasks |
| **CRITIC** | Verify outputs against external sources | Fact-checking, accuracy |
| **Tool augmented** | LLM + external tools | Tasks requiring real-world data |
| **Router** | Route queries to specialized sub-agents | Multi-domain systems |
| **Orchestrator-Worker** | Coordinator delegates to specialist agents | Complex, parallel workflows |
| **Blackboard** | Agents share a common workspace | Collaborative problem-solving |

---

### Q8. What is the Router pattern?

**A:** A **Router** classifies the user's intent and routes the request to the appropriate specialized agent or tool.

```python
def route_query(question: str) -> str:
    classification_prompt = f"""Classify this question into one category:
    - "hr_policy": questions about leaves, benefits, policies
    - "technical": questions about code, systems, tools
    - "general": everything else

    Question: {question}
    Return ONLY the category name."""

    category = llm.invoke(classification_prompt).content.strip()

    if category == "hr_policy":
        return hr_rag_agent(question)
    elif category == "technical":
        return technical_agent(question)
    else:
        return general_agent(question)
```

---

### Q9. What is the Orchestrator-Worker pattern?

**A:**

```
User Goal → Orchestrator (Planner)
                ├── Worker Agent 1: Web Research
                ├── Worker Agent 2: Data Analysis
                ├── Worker Agent 3: Report Writing
                └── Result → Orchestrator → Final Answer
```

**Orchestrator responsibilities:**
1. Decompose the goal into sub-tasks.
2. Assign sub-tasks to appropriate workers.
3. Collect and integrate results.
4. Handle failures (retry, reassign, escalate).
5. Deliver the final answer.

---

### Q10. What is the Reflexion pattern?

**A:** **Reflexion** adds a self-evaluation loop where the agent critiques its own output and generates an improved version.

```
1. Generate initial answer
2. Evaluate: "Is this answer correct, complete, and well-reasoned?"
3. If score < threshold:
   - Identify specific flaws
   - Generate improved answer
4. Repeat until quality threshold is met or max iterations reached
```

---

## 🔹 Section 3 — Tool Management

### Q11. How do you design good tools for agents?

**A:**

| Principle | Good | Bad |
|-----------|------|-----|
| **Single responsibility** | `search_web(query)` | `do_everything(task)` |
| **Clear description** | "Search the internet for current info about X" | "Search" |
| **Validated inputs** | Type hints + Pydantic validation | Untyped `*args` |
| **Graceful errors** | Return error message string | Raise exception (crashes agent) |
| **Deterministic where possible** | Same input → same output | Unpredictable behavior |
| **Atomic** | Does one thing completely | Half-baked operations |

```python
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class SQLQueryInput(BaseModel):
    query: str = Field(description="A valid SELECT SQL query to run against the employee database")

def run_sql(query: str) -> str:
    """Execute a SQL query against the employee database and return results."""
    if not query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for safety."
    try:
        result = db.execute(query)
        return str(result.fetchall())
    except Exception as e:
        return f"SQL Error: {e}"

sql_tool = StructuredTool.from_function(
    func=run_sql,
    name="sql_query",
    description="Query the employee database. Use for structured data about employees, salaries, departments.",
    args_schema=SQLQueryInput
)
```

---

### Q12. What is tool chaining? How does it work?

**A:** **Tool chaining** is when one tool's output feeds into another tool.

```
Agent:
  Action: search_web("Tesla Q2 2026 revenue")
  Observation: "Tesla reported $25.18B revenue in Q2 2026"

  Action: search_web("Tesla Q2 2025 revenue")
  Observation: "Tesla reported $22.50B revenue in Q2 2025"

  Action: calculate("(25.18 - 22.50) / 22.50 * 100")
  Observation: "11.91"

  Final Answer: "Tesla's Q2 2026 revenue was $25.18B, up 11.91% from Q2 2025."
```

The agent **autonomously decides** to chain these tools based on the task requirements.

---

## 🔹 Section 4 — Quick Fire Questions

### Q13. What is an agent's stopping condition?

**A:** When does an agent stop its loop?
1. **Task completed** — LLM signals "Final Answer."
2. **Max iterations reached** — Safety limit (e.g., 10 iterations).
3. **Max tokens reached** — Context window limit.
4. **Error threshold** — Too many consecutive tool failures.
5. **User interruption** — HITL approval denied.

---

### Q14. What is "agentic reasoning" vs "chain of thought"?

**A:**
- **Chain of Thought (CoT):** Internal reasoning within a single LLM response.
- **Agentic reasoning:** Multi-step reasoning across many LLM calls, with actual tool interactions and observations between each step.

CoT is about thinking before answering. Agentic reasoning is about thinking, acting, observing, thinking again, acting again — over many turns.

---

### Q15. What is the "two-agent" pattern?

**A:** One agent writes/proposes; the other agent critiques/reviews.

```
Generator Agent: "Here is my plan: {plan}"
Critic Agent: "Issues with your plan: 1. You missed X. 2. Step 3 is inefficient."
Generator Agent: "Revised plan: {improved_plan}"
Critic Agent: "Approved." OR "Still has issues: ..."
```

Used in AutoGen and similar frameworks. Produces higher-quality outputs than single-agent approaches.

---

> **💡 Viva Tip:** For frameworks, focus on understanding WHEN to use which framework (not memorizing APIs). Show you know the trade-offs: LangChain for general use, LangGraph for complex state, CrewAI for multi-agent roles, AutoGen for code-executing agents.

---

*End of Unit 12 — Agentic AI Frameworks 🔧*
