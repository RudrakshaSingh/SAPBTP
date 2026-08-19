# JouleOps Capstone — Viva Questions & Answers

> A ready-reference for your project demo / viva. Questions are grouped by topic and ordered easy → medium.

---

## 1 · Project Overview

### Q1. Can you give a one-line summary of your capstone project?

**A.** We built **JouleOps**, an Agentic AI enterprise assistant for a fictional company called **NorthWind Manufacturing** that lets plant supervisors, sales managers, and finance controllers ask business questions in plain English — and the AI agent fetches live data from **SAP HANA Cloud** and even takes actions like raising maintenance tickets, all without exposing any database credentials to the LLM.

---

### Q2. What business problem does JouleOps solve?

**A.** NorthWind employees waste 30–45 minutes daily navigating multiple SAP transactions for routine tasks — checking stock levels, pulling sales reports, or chasing overdue invoices. JouleOps eliminates that friction by letting them type a single natural-language question in the **Joule chat** and get an instant, auditable answer backed by real HANA Cloud data.

---

### Q3. Who are the personas in your project?

**A.** There are four personas:

| Persona | Role | Typical Ask |
|---------|------|-------------|
| **Ramesh** | Plant Supervisor (Pune) | "Is steel coil MAT-1023 below safety stock? If yes, raise a ticket." |
| **Priya** | Regional Sales Manager (South) | "Show me last week's open orders for the South region." |
| **Anil** | Finance Controller | "Summarize C-501's overdue invoices and suggest next steps." |
| **Meena** | IT Architect / Sponsor | She sets the 3 security rules the solution must follow. |

---

### Q4. What are Meena's three hard rules?

**A.**
1. **No raw HANA credentials must ever reach the LLM** — only the FastAPI/MCP server holds them.
2. **Every write action must be audited** — a row in `AUDIT_LOG` is created before any response is returned.
3. **Use SAP-native agentic capabilities** — reasoning happens inside the Joule Agent, not a custom chatbot.

---

### Q5. Walk me through the end-to-end data flow of a single request.

**A.**

```
User (plain English)
  → Joule Chat (SAP Build UI)
    → Joule Agent (Joule Studio — intent routing + LLM reasoning)
      → Joule Skill (REST action) OR MCP Tool
        → BTP Destination (HTTP, with sap-joule-studio-* property)
          → Python FastAPI / MCP Server (on port 8000 / 8001)
            → SAP HANA Cloud (parameterized SQL via hdbcli)
              → JSON result flows back up the chain
                → Joule Agent composes a grounded, conversational response
                  → User sees the answer in Joule Chat
```

---

## 2 · Agentic AI — Concepts

### Q6. What is Agentic AI?

**A.** Agentic AI refers to AI systems that can **autonomously plan, decide, and act** to achieve a goal — not just generate text. An agentic system:
- Understands the user's intent,
- Breaks it into sub-tasks,
- Decides *which tools* to call and in *what order*,
- Executes those tools, and
- Composes a final answer using the tool results.

In our project, the **Joule Agent** is the agentic layer — it classifies user queries, picks the right Joule Skill or MCP tool, calls the FastAPI backend, and responds conversationally.

---

### Q7. How is Agentic AI different from a regular chatbot?

**A.**

| Aspect | Regular Chatbot | Agentic AI |
|--------|----------------|------------|
| Reasoning | Single-turn Q&A | Multi-step planning |
| Tools | None — relies on training data | Calls external tools (APIs, databases) |
| Actions | Read-only text | Can perform write operations (create ticket, flag invoice) |
| Grounding | May hallucinate | Answers grounded in live data from source systems |
| Autonomy | User drives every step | Agent decides tool sequence autonomously |

---

### Q8. What is an "agentic workflow"?

**A.** An agentic workflow is the structured pipeline an AI agent follows to fulfill a request:

1. **Intent Classification** — The agent identifies what the user wants (Lookup / Reporting / Action / Escalation).
2. **Planning** — The agent decides which tool(s) to call and with what parameters.
3. **Tool Execution** — The agent invokes the selected Joule Skill or MCP tool, which calls FastAPI → HANA Cloud.
4. **Result Synthesis** — The agent takes the JSON response and composes a human-friendly, grounded answer.
5. **Guardrail Check** — If data is missing or the user lacks permission, the agent explains why instead of failing silently.

In JouleOps, this is handled by the **Joule Studio Agent** with **multi-step reasoning (planner + tool calling)** enabled.

---

### Q9. What agentic workflow did you use in this project specifically?

**A.** We used the **SAP Joule Agent framework** inside **Joule Studio**, which follows a **ReAct-style** (Reasoning + Acting) agentic workflow:

1. The agent receives the user's natural-language query.
2. Its **Intent Router** classifies the query into one of four categories: *Lookup, Reporting, Action, or Escalation*.
3. Based on the classification, the **planner** selects one or more registered tools — either a **Joule Skill** (REST action endpoint) or an **MCP tool**.
4. The agent **extracts parameters** from the query (e.g., material ID, plant code, region) and calls the tool.
5. The tool response (JSON from FastAPI/HANA) is passed back to the agent.
6. The agent applies **business logic reasoning** (e.g., comparing `stock_qty` < `safety_stock` → trigger `create_ticket`).
7. If a multi-step action is needed (e.g., check stock *then* create ticket), the agent **chains tool calls** sequentially.
8. Finally, the agent **synthesizes** a grounded response that includes the tool name, source tables, and masked parameters — ensuring **source transparency**.

---

## 3 · SAP Joule

### Q10. What is SAP Joule?

**A.** **SAP Joule** is SAP's generative AI copilot embedded across SAP applications (SAP Build, S/4HANA, SuccessFactors, etc.). It allows users to interact with enterprise data using natural language. Starting from **Joule Studio (GA January 2026)**, developers can build **custom Joule Agents** with their own tools, skills, and LLM configurations.

---

### Q11. What is Joule Studio?

**A.** **Joule Studio** is the development environment inside SAP Build where you create custom Joule Agents. In Joule Studio, you can:
- Define the agent's **name, description, and system prompt** (instructions),
- Select an **LLM** from SAP's model list,
- Add **Joule Skills** (actions wired to REST APIs via BTP Destinations),
- Connect **MCP Servers** as tool sources,
- Enable **multi-step reasoning** (planner + tool calling),
- Set **guardrails** (e.g., "never invent data").

---

### Q12. What are Joule Skills?

**A.** Joule Skills are the **tools/actions** registered in Joule Studio that the agent can invoke. Each skill maps to a specific REST endpoint exposed through a **BTP Destination**. In our project, we have these Joule Skills:

| Joule Skill | FastAPI Endpoint | Persona |
|-------------|-----------------|---------|
| `get_material_details` | `GET /materials/{id}/{plant}` | Ramesh |
| `get_open_sales_orders` | `GET /sales-orders/open` | Priya |
| `get_customer_summary` | `GET /customers/{id}/summary` | Anil |
| `summarize_overdue_invoices` | `GET /invoices/{id}/overdue-summary` | Anil |
| `create_ticket` | `POST /tickets` | Ramesh |

Each skill is wired to a BTP Destination with the property `sap-joule-studio-action = true` so it's auto-discovered by Joule Studio.

---

### Q13. How does Joule decide which skill to call?

**A.** The Joule Agent uses an **Intent Router** behavior configured in Joule Studio. It classifies every user query as:
- **Lookup** — e.g., "check stock for MAT-1023" → `get_material_details`
- **Reporting** — e.g., "show open orders for South" → `get_open_sales_orders`
- **Action** — e.g., "create a maintenance ticket" → `create_ticket`
- **Escalation** — e.g., missing parameters or VIEWER role → asks clarifying question or refuses politely

The agent's **system prompt** (instruction) explains the personas and rules, guiding the LLM to pick the correct tool.

---

## 4 · MCP (Model Context Protocol)

### Q14. What is MCP?

**A.** **MCP (Model Context Protocol)** is an **open standard** (originally by Anthropic, now widely adopted) that defines how AI models/agents discover and invoke external tools. Think of it as a **"USB-C port for AI"** — a universal interface between an AI agent and the tools it can use.

MCP standardizes:
- **Tool discovery** — the agent auto-discovers available tools and their schemas,
- **Tool invocation** — structured input/output format for calling tools,
- **Transport** — supports SSE (Server-Sent Events) and Streamable HTTP.

---

### Q15. Why did you use MCP in this project?

**A.** Three reasons:
1. **SAP-native support** — Joule Studio natively supports MCP servers via BTP Destinations (set `sap-joule-studio-mcp-server = true`), so tools are auto-discovered.
2. **Decoupling** — MCP separates tool *definitions* from the agent. We can add/remove tools on the MCP server without reconfiguring the Joule agent.
3. **Future-readiness** — MCP is becoming an industry standard. Any MCP-compatible agent (not just Joule) can use our tools.

---

### Q16. How did you implement the MCP server?

**A.** We used the official **`mcp` Python package (FastMCP)** with **Streamable HTTP** transport:

- The server runs on **port 8001** at endpoint `http://127.0.0.1:8001/mcp`.
- We registered 3 tools using the `@mcp.tool()` decorator:
  - `get_inventory_snapshot(plant_code)` — reads `MATERIALS`
  - `get_overdue_invoices(region, days_overdue_min)` — reads `CUSTOMERS` + `INVOICES`
  - `create_ticket(...)` — writes `TICKETS` + `AUDIT_LOG`
- The MCP server **reuses** `app/services.py` — so the same business logic serves both REST and MCP paths.
- It runs **stateless** with `stateless_http=True` and returns `json_response=True`.

---

### Q17. What is the difference between a Joule Skill (REST action) and an MCP tool?

**A.**

| Aspect | Joule Skill (REST Action) | MCP Tool |
|--------|--------------------------|----------|
| **Protocol** | Standard REST/OpenAPI | MCP (Model Context Protocol) |
| **Discovery** | Manual — upload OpenAPI spec to Joule Studio | Automatic — agent discovers tools from MCP endpoint |
| **Governance** | Tighter — each endpoint is explicitly registered | Looser — any tool on the server is available |
| **Coupling** | Agent knows the exact URL and schema | Agent only knows the MCP endpoint; tools are dynamic |
| **BTP Property** | `sap-joule-studio-action = true` | `sap-joule-studio-mcp-server = true` |
| **Best for** | Production, governed APIs | Rapid prototyping, multi-tool discovery |

In our Scenario 4, we demonstrate the **same business need** (inventory snapshot) served through both paths.

---

### Q18. What transport does your MCP server use?

**A.** **Streamable HTTP** — the MCP server runs as a standard HTTP service on port 8001. The agent sends HTTP requests to `/mcp`, and responses are streamed back. We chose this over SSE because it's simpler, stateless, and works well through ngrok tunnels and BTP Destinations.

---

## 5 · Tech Stack & Architecture

### Q19. What is your tech stack?

**A.**

| Layer | Technology |
|-------|-----------|
| **Agent Runtime** | SAP Joule Studio (Agent Builder) on SAP BTP |
| **Database** | SAP HANA Cloud (Trial / Free-Tier) |
| **Action Layer** | Python 3.11+ with FastAPI, Pydantic v2, uvicorn |
| **DB Driver** | `hdbcli` (SAP HANA Python driver) |
| **MCP Server** | Python `mcp` / FastMCP library (Streamable HTTP) |
| **Connectivity** | SAP BTP Destinations |
| **Tunneling** | ngrok (for local demo to SAP BTP) |
| **Data Generation** | Python `faker` library |

---

### Q20. Why FastAPI?

**A.** FastAPI was chosen because:
- **Automatic OpenAPI spec** — Joule Studio needs an OpenAPI 3.0.x document to register skills. FastAPI generates it automatically.
- **Pydantic v2 integration** — request/response validation is built-in, preventing SQL injection and bad data.
- **Async-capable** — though we use synchronous HANA calls, FastAPI can handle concurrent requests efficiently.
- **Developer-friendly** — auto-generated Swagger UI at `/docs` makes testing easy.

We explicitly set `app.openapi_version = "3.0.3"` because SAP Build Actions accepts 3.0.x but not 3.1.0.

---

### Q21. Explain the project folder structure.

**A.**
```
Accentue_capstone/
├── app/                    # FastAPI application
│   ├── main.py             # App entry point, routers, error handler
│   ├── config.py           # Pydantic settings from .env
│   ├── db.py               # HANA Cloud connection (TLS, context manager)
│   ├── models.py           # Pydantic request/response models
│   ├── services.py         # Business logic + parameterized SQL
│   └── routes/             # Route files (materials, sales, customers, tickets)
├── mcp_server/             # MCP server (separate service on port 8001)
│   ├── server.py           # FastMCP tool definitions
│   └── README.md           # MCP-specific docs
├── sql/                    # Database scripts
│   ├── 01_schema.sql       # DDL (6 tables)
│   ├── 02_seed_data.sql    # ~1800+ rows of synthetic data
│   ├── 03_verify.sql       # Row-count verification queries
│   ├── 04_reset_delete.sql # Drop everything for a clean restart
│   └── generate_seed_data.py  # Python Faker script
├── requirements.txt        # Python dependencies
├── .env / .env.sample      # HANA credentials (never committed)
└── README.md               # Project documentation
```

---

### Q22. How does your app connect to SAP HANA Cloud?

**A.** The `app/db.py` module uses the `hdbcli` driver with a **context manager**:

- Credentials are loaded from `.env` via **Pydantic Settings** (`SecretStr` for the password — never printed/logged).
- The connection is **TLS-encrypted** (`encrypt=True`, `sslValidateCertificate=True`).
- `autocommit=False` — so we control transactions explicitly (important for ticket + audit atomicity).
- A **15-second timeout** prevents hanging if HANA Cloud is sleeping.
- The connection is always closed in the `finally` block.

---

## 6 · Database

### Q23. What tables are in your HANA Cloud schema?

**A.** The `JOULEOPS` schema has 6 tables:

| Table | Rows | Purpose |
|-------|------|---------|
| `MATERIALS` | ~500 | Stock levels, safety stock, plant-wise |
| `CUSTOMERS` | ~100 | B2B customers with credit limits |
| `SALES_ORDERS` | ~800 | Orders with status, region, dates |
| `INVOICES` | ~400 | Invoices with overdue tracking |
| `TICKETS` | 0 (initially) | Maintenance tickets created by the agent |
| `AUDIT_LOG` | 0 (initially) | Audit trail for every write operation |

Every table has `CREATED_ON`, `UPDATED_ON`, and `SOURCE_SYSTEM` audit fields.

---

### Q24. How did you generate the seed data?

**A.** We wrote a Python script (`sql/generate_seed_data.py`) using the **Faker** library. It generates realistic but synthetic data matching the NorthWind story — Indian plant codes (PLT-PUN, PLT-CHN, PLT-HYD, PLT-CBE), Indian region names, and realistic material descriptions. The script outputs `02_seed_data.sql` which is then run in the HANA SQL Console.

---

### Q25. How do you prevent SQL injection?

**A.** Two layers:
1. **Parameterized queries** — every SQL query uses `?` placeholders with `cursor.execute(sql, (param1, param2))`. We **never** use string concatenation for user values.
2. **Pydantic validation** — all inputs are validated with `StringConstraints` (min/max length, stripping whitespace) and typed enums (`TicketPriority`, `UserRole`) before they reach the service layer.

---

## 7 · Security & RBAC

### Q26. How do you ensure HANA credentials never reach the LLM?

**A.**
- Credentials live **only** in the `.env` file on the server, loaded via `pydantic-settings` as `SecretStr`.
- The FastAPI/MCP server is the **only** component that connects to HANA.
- The Joule Agent only sees **tool signatures** (parameter names/types) and **JSON responses** — never connection strings or passwords.
- The `ServiceError` exception handler strips SQL errors and returns only safe messages like *"The material lookup operation could not be completed in SAP HANA Cloud"*.

---

### Q27. How does RBAC work in your project?

**A.** We simulate role-based access control using the `X-User-Role` HTTP header:

- The header accepts one of: `PLANT_SUPERVISOR`, `SALES_MANAGER`, `FINANCE`, `VIEWER`.
- The `create_ticket` endpoint checks the role **before** any database write.
- If the role is `VIEWER`, the system:
  1. Inserts an `AUDIT_LOG` row with `outcome = 'DENIED'`,
  2. Returns HTTP 403 with message: *"VIEWER is not allowed to create maintenance tickets"*.
- All other roles can create tickets.

---

### Q28. How does audit logging work?

**A.** Every call to `create_ticket` (whether it succeeds or fails) inserts a row in `AUDIT_LOG`:

| Field | Value |
|-------|-------|
| `LOG_ID` | UUID |
| `TS` | Current UTC timestamp |
| `USER_ROLE` | The role from the header (e.g., `PLANT_SUPERVISOR`) |
| `TOOL_NAME` | Always `"create_ticket"` |
| `PARAMS_MASKED` | JSON with the description field replaced by `"***MASKED***"` |
| `OUTCOME` | `SUCCESS`, `FAILURE`, or `DENIED` |

The ticket insert and audit insert happen in the **same database transaction** — if either fails, both roll back.

---

## 8 · API Endpoints

### Q29. List all your FastAPI endpoints and what they do.

**A.**

| Method | Path | Purpose | Tables |
|--------|------|---------|--------|
| `GET` | `/materials/{material_id}/{plant_code}` | Check stock vs. safety stock | `MATERIALS` |
| `GET` | `/sales-orders/open` | Open orders grouped by customer | `SALES_ORDERS`, `CUSTOMERS`, `MATERIALS` |
| `GET` | `/customers/{customer_id}/summary` | Customer profile + invoice exposure | `CUSTOMERS`, `INVOICES` |
| `GET` | `/invoices/{customer_id}/overdue-summary` | Overdue analysis + recommendation | `CUSTOMERS`, `INVOICES` |
| `POST` | `/tickets` | Create a maintenance ticket (audited) | `MATERIALS`, `TICKETS`, `AUDIT_LOG` |

---

### Q30. How does the overdue invoice recommendation logic work?

**A.** The `summarize_overdue_invoices` service applies a simple rule engine:

```
if no overdue invoices       → NO_ACTION
elif oldest_days_overdue > 90 → ESCALATE_TO_LEGAL
elif oldest_days_overdue >= 60 OR credit_utilization >= 80% → HOLD_FURTHER_SHIPMENTS
else                          → SEND_REMINDER
```

The credit utilization is calculated as `(outstanding_amount / credit_limit) × 100`. This gives Anil an actionable recommendation without him opening Excel.

---

## 9 · MCP Server — Deeper Dive

### Q31. List the 3 MCP tools and their source tables.

**A.**

| MCP Tool | Parameters | Source Tables |
|----------|-----------|---------------|
| `get_inventory_snapshot` | `plant_code` | `MATERIALS` |
| `get_overdue_invoices` | `region`, `days_overdue_min` | `CUSTOMERS`, `INVOICES` |
| `create_ticket` | `material_id`, `plant_code`, `priority`, `assigned_team`, `description`, `user_role` | `MATERIALS`, `TICKETS`, `AUDIT_LOG` |

---

### Q32. How does the MCP server ensure source transparency?

**A.** Every MCP tool response is wrapped in a `_tool_result()` envelope that includes:
```json
{
  "tool": "get_inventory_snapshot",
  "source_tables": ["MATERIALS"],
  "parameters": {"plant_code": "PLT-CHN"},
  "result": { ... actual data ... }
}
```

This way, the Joule Agent can tell the user exactly which tool was called, which HANA tables were queried, and what parameters were used — with sensitive values masked.

---

### Q33. Does the MCP server duplicate the FastAPI business logic?

**A.** **No.** The MCP server **imports and reuses** `app/services.py`. Both the REST routes and MCP tools call the same service functions (`services.get_inventory_snapshot()`, `services.create_ticket()`, etc.). This avoids code duplication and ensures consistent behavior regardless of which path is used.

---

## 10 · Demo Scenarios

### Q34. Explain Scenario 1 (Ramesh's stock check + auto-ticket).

**A.** Ramesh asks: *"Is steel coil MAT-1023 below safety stock in Pune? If yes, raise a HIGH-priority ticket."*

1. Agent classifies intent → **Lookup + Action**.
2. Calls `get_material_details("MAT-1023", "PLT-PUN")`.
3. FastAPI queries `MATERIALS` table → returns `stock_qty=12`, `safety_stock=50`, `below_safety_stock=true`.
4. Agent sees stock is below safety → chains to `create_ticket(material_id="MAT-1023", plant_code="PLT-PUN", priority="HIGH", assigned_team="Mechanical", description="...")`.
5. FastAPI inserts into `TICKETS` + `AUDIT_LOG` in one transaction → returns `ticket_id="TKT-00045"`.
6. Agent responds: *"Stock is 12 units (safety = 50). Ticket TKT-00045 created. Source: MATERIALS, TICKETS."*

This demonstrates **multi-step tool chaining** — the agent autonomously decides to call a second tool based on the first tool's result.

---

### Q35. Explain Scenario 4 (MCP vs. REST comparison).

**A.** The user asks: *"Give me an inventory snapshot for the Chennai plant."*

- The agent routes to **Lookup** and picks the **MCP tool** `get_inventory_snapshot("PLT-CHN")` instead of a Joule Skill.
- The MCP server calls the same `services.get_inventory_snapshot()` function as the REST endpoint would.
- The response reaches the agent through the MCP protocol instead of REST.

**Trade-offs documented:**
- **REST (Joule Skill):** More governed, each endpoint explicitly registered, better for production.
- **MCP:** Auto-discovered, more decoupled, better for rapid iteration and multi-agent setups.

---

### Q36. What happens in Scenario 5 (Escalation/Guardrail demo)?

**A.** User says: *"Create a ticket."* (no details given)

- The agent detects **missing required parameters** (material, plant, priority, team).
- Instead of guessing or sending nulls, it asks a **single clarifying question**: *"Which material, plant, priority, and team should I use?"*
- If the user has role = `VIEWER`, the agent refuses: *"VIEWER role is not authorized to create tickets."* — no FastAPI call is made.

This demonstrates the agent's **guardrails**: never invent data, validate inputs, and enforce RBAC.

---

## 11 · BTP & Deployment

### Q37. What are BTP Destinations and why do you need them?

**A.** **BTP Destinations** are SAP's way of securely registering external HTTP endpoints so that BTP services (like Joule Studio) can call them. We create two destinations:

1. **FastAPI Destination** — points to the FastAPI service (port 8000 or ngrok URL) with property `sap-joule-studio-action = true`.
2. **MCP Destination** — points to the MCP server (port 8001 or ngrok URL) with property `sap-joule-studio-mcp-server = true`.

These properties are what make the endpoints **discoverable** inside Joule Studio's Agent Builder.

---

### Q38. How do you expose your local server to SAP BTP for demo?

**A.** We use **ngrok** to create a secure HTTPS tunnel:
```bash
ngrok http 8000 --host-header=rewrite   # for FastAPI
ngrok http 8001 --host-header=rewrite   # for MCP
```
The ngrok free plan only supports 1 tunnel at a time, so we stop one before starting the other. The generated HTTPS URL is then registered as a BTP Destination.

---

## 12 · General Agentic AI & Conceptual Questions

### Q39. What is the difference between AI, Generative AI, and Agentic AI?

**A.**

| Type | What It Does | Example |
|------|-------------|---------|
| **Traditional AI** | Pattern recognition, classification | Spam filter, image recognition |
| **Generative AI** | Creates new content (text, images, code) | ChatGPT generating an email |
| **Agentic AI** | Autonomously plans, reasons, uses tools, and takes actions | JouleOps checking stock, deciding it's low, and raising a ticket — all in one flow |

Agentic AI builds *on top of* generative AI by adding **tool use, planning, and autonomous action**.

---

### Q40. What does "grounded response" mean?

**A.** A grounded response is one that is **backed by actual data** from a source system (HANA Cloud in our case) rather than generated from the LLM's training data. If the tool returns no data, the agent says *"No records found in HANA Cloud for the given filters"* instead of making something up. Every response also includes which tool and tables were used — that's source transparency.

---

### Q41. What is tool calling / function calling in the context of LLMs?

**A.** Tool calling is when an LLM, instead of generating a free-text answer, outputs a **structured request** to invoke an external function — specifying the function name and parameters. The runtime (Joule Studio in our case) executes the function and feeds the result back to the LLM, which then composes the final response. This is how LLMs interact with real-world data and systems.

---

### Q42. What is multi-step reasoning?

**A.** Multi-step reasoning means the agent can **chain multiple tool calls** in sequence to fulfill a single request. For example, Ramesh's request requires:
1. First call `get_material_details` to check stock,
2. Then, *based on the result*, call `create_ticket` if stock is low.

The agent plans this sequence autonomously — the user doesn't have to ask twice. In Joule Studio, this is enabled by turning on the **planner + tool calling** option.

---

### Q43. What is an Intent Router?

**A.** An Intent Router is a classification layer in the agent that categorizes each user query into a predefined intent:
- **Lookup** — single record retrieval (e.g., check stock for one material)
- **Reporting** — aggregated data (e.g., open orders by region)
- **Action** — write operation (e.g., create a ticket)
- **Escalation** — missing info or unauthorized access

The intent determines which tool the agent considers first, making tool selection faster and more accurate.

---

### Q44. How is Pydantic used in this project?

**A.** Pydantic is used in multiple ways:
- **Request validation**: `CreateTicketRequest` model validates material_id, plant_code, priority (enum), and description before they reach the service layer.
- **Response serialization**: Models like `MaterialResponse`, `SalesOrdersResponse` define the exact JSON shape returned to the agent.
- **Settings management**: `pydantic-settings` loads HANA credentials from `.env` with type validation and `SecretStr` for the password.
- **String constraints**: `StringConstraints(min_length=1, max_length=20)` prevents empty or oversized inputs.
- **Extra = forbid**: The `JouleOpsModel` base class rejects unexpected fields, hardening the API.

---

### Q45. What happens if SAP HANA Cloud is not reachable?

**A.** The `db.py` context manager catches `dbapi.Error` and raises a custom `DatabaseConnectionError`. The service layer catches this and raises `DatabaseOperationError` (HTTP 503) with a safe message: *"The {operation} operation could not be completed in SAP HANA Cloud"*. No stack traces, SQL errors, or credentials are ever exposed to the caller.

---

## 13 · Quick-Fire Questions

### Q46. What port does FastAPI run on?
**A.** Port **8000**.

### Q47. What port does the MCP server run on?
**A.** Port **8001**, at endpoint `/mcp`.

### Q48. What Python version does the project require?
**A.** Python **3.11+** (verified with Python 3.14.6).

### Q49. What database driver do you use?
**A.** `hdbcli` — the official SAP HANA Python driver.

### Q50. What is the OpenAPI version you use and why?
**A.** OpenAPI **3.0.3** — because SAP Build Actions accepts 3.0.x but does not accept 3.1.0.

### Q51. How many plants does NorthWind have?
**A.** 4 plants — Pune (PLT-PUN), Chennai (PLT-CHN), Hyderabad (PLT-HYD), and Coimbatore (PLT-CBE).

### Q52. What does the `_equipment_id()` function do?
**A.** It generates a deterministic equipment ID from the material ID and plant code (e.g., `EQ-PLT-PUN-MAT-1023`). If the result exceeds 30 characters, it falls back to a SHA-256 hash prefix to stay within the column size.

---

> **Tip:** Read through this document 2-3 times before your viva. Focus on understanding the *flow* (Q5, Q8, Q9) and the *why* behind each design decision — those are the questions seniors love to dig into. Good luck! 🚀
