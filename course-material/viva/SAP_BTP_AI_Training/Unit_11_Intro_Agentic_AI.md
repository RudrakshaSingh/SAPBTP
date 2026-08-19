# 🤖 Unit 11 — Introduction to Agentic AI

> **Module**: Module 5 — Agentic AI  
> **Duration**: Day 20–21 (16 hours)  
> **Dates**: 24-Jul-2026, 27-Jul-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — What is Agentic AI?

### Q1. What is Agentic AI? How does it differ from basic LLM usage?

**A:** **Agentic AI** refers to AI systems that can **perceive their environment, reason about goals, plan actions, and execute tasks autonomously** — often over multiple steps — without needing a human to guide every step.

| Aspect | Basic LLM | Agentic AI |
|--------|----------|-----------|
| **Interaction** | Single prompt → single response | Multi-step; takes actions across many turns |
| **Tools** | None; only generates text | Can use tools (search, code, APIs) |
| **Planning** | No; one-shot answer | Yes; decomposes goals into sub-tasks |
| **Memory** | No persistent memory | Can maintain context and learn |
| **Autonomy** | Zero; human controls every step | High; works independently toward a goal |
| **Loop** | One forward pass | Observe → Reason → Act → Observe... (loop) |

**Example difference:**
- **Basic LLM:** "Write me Python code for a web scraper." → Gives code.
- **AI Agent:** "Research the top 5 AI tools, compare them, and write a report." → Searches the web, reads pages, synthesizes, writes report — all autonomously.

---

### Q2. What are the core components of an AI agent?

**A:** An AI agent has four key components:

| Component | What It Does | Example |
|-----------|-------------|---------|
| **Perception** | Observe the environment; receive inputs | Read user query, receive tool output |
| **Memory** | Store and retrieve information | Conversation history, retrieved documents |
| **Reasoning** | Decide what to do next | "I need to search for X before answering Y" |
| **Action** | Execute decisions via tools | Call search API, run Python code, call another LLM |

**The loop:**
```
Input → [Perceive] → [Reason] → [Act] → [Observe result] → [Reason] → [Act] → ... → [Final Answer]
```

---

### Q3. What is the difference between a chatbot, a copilot, and an agent?

**A:**

| Type | Autonomy | Tool Use | Planning | Memory | Example |
|------|---------|----------|---------|--------|---------|
| **Chatbot** | None (follows scripts) | ❌ | ❌ | None | FAQ bot |
| **LLM assistant** | Low (one-shot response) | ❌ | ❌ | Per session | ChatGPT basic |
| **Copilot** | Medium (assists human) | Limited | ❌ | Per session | GitHub Copilot |
| **AI Agent** | High (autonomous) | ✅ | ✅ | Long-term | AutoGPT, LangGraph agent |

---

### Q4. What is the ReAct (Reasoning + Acting) pattern?

**A:** **ReAct** is the foundational agentic pattern where the agent alternates between **thinking** (reasoning about what to do) and **acting** (using a tool), forming a loop until the task is complete.

```
Question: "What is the current price of Apple stock and how has it changed this week?"

Thought 1: I need to find the current Apple stock price.
Action 1: Search("AAPL stock price today")
Observation 1: AAPL is trading at $227.82

Thought 2: Now I need the price from a week ago.
Action 2: Search("AAPL stock price one week ago")
Observation 2: AAPL was at $219.50 one week ago

Thought 3: I can now calculate the change.
Action 3: Calculator("(227.82 - 219.50) / 219.50 * 100")
Observation 3: 3.79%

Thought 4: I have all the information I need.
Final Answer: Apple stock is currently at $227.82, up 3.79% from $219.50 a week ago.
```

**Why ReAct works:**
- **Transparency** — You can see exactly why the agent took each action.
- **Debuggable** — When something goes wrong, you can trace the reasoning.
- **Grounded** — Actions are based on observations, not pure hallucination.

---

### Q5. What are agent tools? Give examples.

**A:** **Tools** are functions/APIs that an agent can call to interact with the world beyond text generation.

| Category | Tools | What They Do |
|----------|-------|-------------|
| **Search** | Google Search, Bing, Tavily, DuckDuckGo | Find current information on the web |
| **Code execution** | Python REPL, E2B sandbox | Run code, do calculations, data analysis |
| **File I/O** | Read/write files, PDFs | Access documents |
| **Database** | SQL query tool | Query structured databases |
| **APIs** | HTTP request tool | Call any REST API |
| **Vector store** | Similarity search | RAG retrieval |
| **Communication** | Email, Slack, calendar | Send messages, schedule meetings |
| **Browser** | Playwright, Selenium | Navigate web pages, fill forms |
| **LLM calls** | Sub-agents, specialists | Delegate to other LLMs |

```python
from langchain.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input should be a valid Python expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# Agent decides when to call this tool based on the task
```

---

### Q6. What is an agent's memory? What types exist?

**A:**

| Memory Type | Duration | What It Stores | Example |
|-------------|----------|----------------|---------|
| **In-context (working)** | Current session | Recent messages, tool results | Conversation buffer |
| **Short-term external** | Session | Structured task state | Variables in the agent's loop |
| **Long-term (persistent)** | Across sessions | User preferences, learned facts | Vector store, database |
| **Episodic** | Experiences | Past task outcomes | "Last time I searched X, result was Y" |
| **Semantic** | Facts | Domain knowledge | Knowledge base |
| **Procedural** | Skills | How to do tasks | Fine-tuned behaviors |

```python
# LangChain conversation memory
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(k=5)  # Remember last 5 exchanges
# Automatically adds to agent's context on each invocation
```

---

## 🔹 Section 2 — Agentic Architectures

### Q7. What are single-agent vs multi-agent systems?

**A:**

| Aspect | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| **Structure** | One LLM with tools | Multiple specialized LLMs |
| **Complexity** | Simpler | More complex |
| **Parallelism** | Sequential only | Can run agents in parallel |
| **Specialization** | Generalist | Each agent specializes |
| **Failure** | One point of failure | More resilient |
| **Use case** | Simple to medium tasks | Complex, multi-domain tasks |

**Multi-agent example:**
```
Orchestrator Agent
    ├── Research Agent (specializes in web search)
    ├── Data Analysis Agent (specializes in Python code)
    ├── Writing Agent (specializes in report writing)
    └── Review Agent (checks and validates the output)
```

---

### Q8. What is an orchestrator agent?

**A:** An **orchestrator** is an agent that coordinates other agents. It breaks down high-level goals into sub-tasks and delegates them to specialized sub-agents.

```
User: "Analyze Q2 sales data and write an executive summary."

Orchestrator:
  1. Delegate to Data Agent: "Load and analyze Q2_sales.csv"
  2. Receive: Statistical analysis results
  3. Delegate to Insights Agent: "Identify key trends from this analysis"
  4. Receive: Trend insights
  5. Delegate to Writing Agent: "Write executive summary from these insights"
  6. Receive: Draft summary
  7. Return summary to user
```

---

### Q9. What is the Plan-and-Execute pattern?

**A:** Rather than deciding one step at a time (ReAct), **Plan-and-Execute** creates a complete plan first, then executes it step by step.

```
Step 1: PLAN
  Question: "Research top 5 competitors and compare pricing"
  Plan:
    1. Search for "top competitors in [industry]"
    2. For each competitor, search for their pricing page
    3. Extract pricing from each page
    4. Create comparison table
    5. Write analysis

Step 2: EXECUTE each plan step sequentially
```

**Plan-and-Execute vs ReAct:**

| Aspect | ReAct | Plan-and-Execute |
|--------|-------|-----------------|
| Planning | Implicit (step-by-step) | Explicit upfront plan |
| Flexibility | Can adapt as it goes | May struggle with unexpected results |
| Transparency | Thought-by-thought | Upfront plan visible |
| Complex tasks | May lose track | Better for multi-step tasks |

---

### Q10. What is self-reflection in AI agents?

**A:** **Self-reflection** is when an agent evaluates and critiques its own outputs before returning them.

```
Agent generates answer
    ↓
Reflection step: "Is this answer correct? Is it complete? Did I miss anything?"
    ↓
If deficient → Generate improved answer
    ↓
Final answer returned
```

**Implementations:**
- **Self-critique:** Same LLM checks its own output against criteria.
- **Separate critic LLM:** Different model evaluates the output.
- **LangGraph reflexion loop:** Graph node that checks and rewrites.

---

## 🔹 Section 3 — Key Agentic Concepts

### Q11. What is tool calling vs function calling?

**A:** These terms are often used interchangeably. **Function calling** (OpenAI term) / **tool calling** is the ability for an LLM to:
1. Recognize when it needs to use a tool.
2. Generate a structured call with arguments.
3. Receive the tool's result.
4. Incorporate the result into its response.

```python
# Define a tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 28°C, Partly cloudy"

# LLM sees the tool definition and decides to call it:
# → {"tool": "get_weather", "arguments": {"city": "Mumbai"}}
# Your code calls: get_weather("Mumbai")
# → "Weather in Mumbai: 28°C, Partly cloudy"
# LLM incorporates result into final answer
```

---

### Q12. What is "tool selection" in agents?

**A:** The LLM must decide **which tool to use (or none)** for each step. This is one of the hardest parts of agents.

**How the LLM selects tools:**
1. It reads the tool **descriptions** (docstrings).
2. It matches the current task to the most appropriate tool.
3. It generates the correct arguments for that tool.

**Why good tool descriptions matter:**
```python
# Bad description → Agent uses tool incorrectly
@tool
def search(query: str) -> str:
    """Search."""  # Too vague!

# Good description → Agent uses tool correctly
@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use this when you need
    facts that may have changed after your training cutoff, or when
    you need specific data you don't know. Input: search query string."""
```

---

### Q13. What is the "observation" step in agentic loops?

**A:** After taking an action (calling a tool), the agent receives an **observation** — the tool's output. This observation is added to the agent's context so it can reason about the result and decide the next step.

```
[Thought]: I need to check the stock price.
[Action]: search("AAPL stock price")
[Observation]: "AAPL is trading at $227.82 as of 2:30 PM ET"  ← tool output

[Thought]: I have the current price. Now I need last week's price.
[Action]: search("AAPL stock price one week ago")
[Observation]: "AAPL closed at $219.50 on July 15"

[Thought]: Now I can calculate the change and answer.
[Final Answer]: "Apple stock is at $227.82, up 3.79% from last week."
```

---

### Q14. What are the risks of autonomous agents?

**A:**

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Infinite loops** | Agent keeps calling tools without converging | Max iteration limit |
| **Hallucinated actions** | Agent "invents" tool calls with wrong arguments | Strong type validation |
| **Prompt injection** | Malicious data in tool output hijacks agent | Output sanitization |
| **Excessive cost** | Too many LLM/API calls | Budget limits, token limits |
| **Side effects** | Agent sends emails, deletes files, purchases items | Human-in-the-loop approval for irreversible actions |
| **Error propagation** | Wrong intermediate result leads to wrong final answer | Error handling, verification steps |
| **Over-trust** | Agent trusts web search results blindly | Source verification |

---

## 🔹 Section 4 — Human-in-the-Loop

### Q15. What is Human-in-the-Loop (HITL) in agentic systems?

**A:** **HITL** means pausing the agent at key decision points to get human approval before proceeding — especially for irreversible actions.

```
Agent: "I'll book a flight to Delhi and charge your credit card ₹12,000"
       → PAUSE: "Do you approve this action? Yes/No"
Human: "Yes"
Agent: Proceeds with booking

Agent: "I'll delete all files in /uploads/old-data/"
       → PAUSE: "This will permanently delete 1,243 files. Confirm?"
Human: "No, skip this step."
Agent: Continues with next task
```

**When HITL is critical:**
- Irreversible actions (delete, send, purchase).
- High-stakes decisions (medical, financial, legal).
- Actions with external impact (emails, social media posts).
- Novel situations the agent hasn't seen before.

---

### Q16. What is the difference between full autonomy and semi-autonomy in agents?

**A:**

| Mode | Human Role | Risk Level | Use Case |
|------|-----------|-----------|----------|
| **Full autonomy** | None; agent acts freely | High | Fully trusted, low-risk automated tasks |
| **Semi-autonomy** | Approves major actions | Medium | Most enterprise AI agents |
| **Supervised** | Reviews and approves every action | Low | High-stakes tasks, new deployments |
| **Assisted** | Human does the work; agent suggests | Very Low | Current copilots (GitHub Copilot) |

---

## 🔹 Section 5 — Agentic Patterns & Use Cases

### Q17. What are common agentic AI use cases?

**A:**

| Domain | Use Case | Agent Capabilities Used |
|--------|---------|------------------------|
| **Customer Service** | Resolve customer complaints end-to-end | Knowledge lookup + CRM update + email |
| **Software Dev** | Debug → fix → test → commit | Code analysis + code writing + test runner |
| **Data Analysis** | "Analyze this dataset and report insights" | Code execution + chart generation + writing |
| **Research** | Competitive analysis, literature review | Web search + reading + summarization |
| **HR** | Screen resumes, schedule interviews | Document reading + email + calendar |
| **Finance** | Automate financial reporting | SQL queries + calculations + report writing |
| **SAP** | Automate SAP transactions via Joule | SAP API calls + business logic + user response |

---

### Q18. What is the difference between a workflow and an agent?

**A:**

| Aspect | Workflow | Agent |
|--------|----------|-------|
| **Control flow** | Pre-defined (static) | Dynamic (decided by LLM) |
| **Flexibility** | Low; follows fixed steps | High; adapts to situation |
| **Predictability** | High; always same steps | Lower; may take different paths |
| **Reliability** | More reliable | Less reliable (can go off-track) |
| **Best for** | Known, repeatable tasks | Novel, open-ended tasks |

**Rule:** Use a **workflow** when you know the exact steps. Use an **agent** when you can't predict all the steps needed.

---

### Q19. What is long-horizon task execution?

**A:** **Long-horizon** refers to tasks that require many steps over a long period, potentially involving multiple tools, decisions, and sub-goals.

**Example of a long-horizon agent task:**
```
Goal: "Conduct market research on the EV industry, produce a 5-page report,
       and schedule a meeting to present it."

Steps needed (~20+):
1-5:   Web searches for EV market data
6-8:   Read and summarize each article
9-11:  Collect statistics (market size, growth, key players)
12-15: Synthesize insights, write report sections
16:    Format the report in the correct template
17:    Save report to SharePoint
18:    Access calendar, find available slots
19:    Send meeting invitation to stakeholders
20:    Confirm meeting was scheduled
```

This requires **sustained reasoning** and **state management** across many steps.

---

## 🔹 Section 6 — Quick Fire Questions

### Q20. What is an "escape hatch" in agent design?

**A:** An **escape hatch** is a mechanism that stops the agent when it's stuck or misbehaving — a safety valve. Examples:
- Maximum iteration limit (`max_iterations=10`).
- Maximum token budget.
- "I don't know" fallback when confidence is low.
- Human intervention trigger when agent signals confusion.

---

### Q21. What is context window management in agents?

**A:** As agents run many steps, the context window fills up with thoughts, actions, and observations. Management strategies:
- **Summarization:** Compress older history into a summary.
- **Truncation:** Drop oldest messages (but may lose important context).
- **External memory:** Store observations in a database, retrieve when needed.
- **Sliding window:** Keep only the last N exchanges in context.

---

### Q22. What is the difference between a tool and a sub-agent?

**A:**
- **Tool:** A deterministic function that takes inputs and returns outputs (web search, calculator, database query).
- **Sub-agent:** Another LLM that can reason, plan, and use tools of its own — more autonomous and flexible.

When a task requires intelligence (not just data retrieval), delegate to a sub-agent. When a task is a simple operation, use a tool.

---

### Q23. What are guardrails in agentic systems?

**A:** **Guardrails** for agents specifically include:
- **Input guards** — Filter malicious queries before they reach the agent.
- **Action guards** — Prevent certain tools from being called (no `rm -rf`).
- **Output guards** — Check generated responses for harmful content.
- **Iteration limits** — Stop runaway agent loops.
- **Budget limits** — Stop after N API calls or N tokens.
- **HITL checkpoints** — Pause and ask human before irreversible actions.

---

### Q24. How do agents handle failures?

**A:**

```python
# Robust agent error handling:
def execute_tool_safely(tool_fn, **kwargs):
    for attempt in range(3):
        try:
            result = tool_fn(**kwargs)
            return result
        except ToolError as e:
            if attempt == 2:
                return f"Tool failed after 3 attempts: {e}"
            time.sleep(2 ** attempt)  # Exponential backoff
```

**Agent-level failure handling:**
1. **Retry** — Try the same action again.
2. **Alternative tool** — Use a different tool for the same goal.
3. **Decompose** — Break the failing step into smaller steps.
4. **Escalate** — Ask human for help.
5. **Graceful failure** — Report what was completed and what failed.

---

> **💡 Viva Tip:** Agentic AI is the most exciting and complex topic. Show you understand the **fundamental loop** (Perceive → Reason → Act → Observe) and the **practical challenges** (loops, cost, reliability). The evaluator wants to see you understand both capabilities AND limitations.

---

*End of Unit 11 — Introduction to Agentic AI 🤖*
