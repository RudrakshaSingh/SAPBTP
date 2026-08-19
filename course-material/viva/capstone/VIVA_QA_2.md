# JouleOps Capstone — Viva Questions Part 2

> Mapped to the **4 Viva Evaluation Parameters**:
> - **[F]** Understanding of Problem Statement
> - **[G]** Answers related to Coding/Configurations
> - **[H]** Understanding of Basic Concepts
> - **[I]** Understanding of Advanced Concepts
>
> Dropdown scoring: **Good** (Strong understanding) · **Fair** (Adequate with gaps) · **No Basis** (Insufficient)

---

## Section A — Understanding of Problem Statement [F]

### Q1. What is the core pain point NorthWind employees face, and how does JouleOps solve it?

**A.** NorthWind employees (Ramesh, Priya, Anil) waste 30–45 minutes daily navigating multiple SAP transactions for routine tasks — checking stock, pulling reports, chasing overdue invoices. JouleOps eliminates that friction by letting them type a single natural-language question in the **Joule chat** and get an instant, auditable answer backed by real HANA Cloud data — including write actions like ticket creation.

---

### Q2. Explain Meena's 3 hard rules. For each rule, explain WHERE in your project it is enforced.

**A.**

| Rule | What It Says | Where Enforced |
|------|-------------|----------------|
| **Rule 1** — No raw HANA credentials reach the LLM | Only the FastAPI/MCP server holds credentials | `db.py` uses `SecretStr`; Joule Agent only sees tool signatures + JSON responses; `ServiceError` handler strips SQL errors |
| **Rule 2** — Every write must be audited | Each `create_ticket` call inserts an `AUDIT_LOG` row | `services.py` → `_insert_audit()` is called for SUCCESS, FAILURE, and DENIED outcomes, in the same transaction |
| **Rule 3** — Use SAP-native agentic capabilities | Reasoning happens inside the Joule Agent, not a custom chatbot | Agent is built in Joule Studio with planner + tool calling; no custom orchestrator |

---

### Q3. Walk through Scenario 1 (Ramesh) end-to-end. What agentic capabilities does it demonstrate?

**A.** Ramesh asks: *"Is steel coil MAT-1023 below safety stock in Pune? If yes, raise a HIGH-priority ticket."*

1. **Intent Classification** → Agent classifies as **Lookup + Action** (multi-intent).
2. **First tool call** → `get_material_details("MAT-1023", "PLT-PUN")`.
3. **FastAPI execution** → Parameterized SQL on `MATERIALS` → returns `stock_qty=12`, `safety_stock=50`, `below_safety_stock=true`.
4. **Agent reasoning** → Sees `below_safety_stock=true` → decides to chain a second tool call.
5. **Second tool call** → `create_ticket(material_id="MAT-1023", plant_code="PLT-PUN", priority="HIGH", assigned_team="Mechanical", description="...")`.
6. **FastAPI execution** → Validates material exists, inserts into `TICKETS` + `AUDIT_LOG` in one transaction → returns `ticket_id="TKT-00045"`.
7. **Response synthesis** → *"Stock is 12 units (safety = 50). Ticket TKT-00045 created. Source: MATERIALS, TICKETS."*

**Agentic capabilities demonstrated**:
- Multi-step reasoning (planner chains two tools)
- Conditional logic (only creates ticket *if* stock is low)
- Source transparency (cites tables in response)
- Audit compliance (AUDIT_LOG row created)

---

### Q4. Walk through Scenario 2 (Priya). What SQL joins are involved and why?

**A.** Priya asks: *"Show me last week's open sales orders for the South region, grouped by customer, with totals."*

1. Agent classifies → **Reporting**.
2. Calls `get_open_sales_orders(region="South", date_from=last_monday, date_to=last_sunday)`.
3. The SQL in `services.py` does a **3-way JOIN**:
   - `SALES_ORDERS SO` (filters by region, status='OPEN', date range)
   - `INNER JOIN CUSTOMERS C ON C.CUSTOMER_ID = SO.CUSTOMER_ID` (gets customer name)
   - `INNER JOIN MATERIALS M ON M.MATERIAL_ID = SO.MATERIAL_ID` (gets unit_price for value calculation)
4. Groups by `CUSTOMER_ID, C.NAME` and calculates `SUM(QTY)`, `SUM(QTY * UNIT_PRICE)`.
5. Orders by `TOTAL_VALUE DESC`.
6. Agent renders a tabular response with customer name, order count, and total value.

**Why 3 tables?** The problem statement says Priya wants "grouped by customer, with totals" — we need CUSTOMERS for names and MATERIALS for price to compute monetary value.

---

### Q5. Walk through Scenario 3 (Anil). How does the recommendation tie back to the problem statement?

**A.** Anil asks: *"Summarize C-501's overdue invoices and tell me what to do next."*

1. Agent classifies → **Reporting + Summarization**.
2. Calls `summarize_overdue_invoices("C-501")`.
3. Internally, this calls `get_customer_summary("C-501")` first — which queries `CUSTOMERS` + `INVOICES`.
4. It calculates: total overdue amount, oldest invoice age, credit utilization %.
5. Applies the rule engine:
   - If oldest > 90 days → `ESCALATE_TO_LEGAL`
   - If oldest >= 60 days OR utilization >= 80% → `HOLD_FURTHER_SHIPMENTS`
   - Otherwise → `SEND_REMINDER`
6. Agent responds: *"C-501 has ₹4.2L overdue (3 invoices, oldest 85 days). Credit utilization at 72%. Recommendation: HOLD_FURTHER_SHIPMENTS."*

**Problem statement tie-back**: Persona 3 says Anil wants *"a suggested next collection step, without opening Excel"* — the rule engine provides exactly that.

---

### Q6. Walk through Scenario 4 (MCP vs REST). What architectural insight does it prove?

**A.** User asks: *"Give me an inventory snapshot for the Chennai plant."*

- **Via MCP**: Agent picks MCP tool `get_inventory_snapshot("PLT-CHN")` → MCP server → `services.get_inventory_snapshot()` → HANA → response via MCP protocol.
- **Via REST (alternative)**: The same data could be fetched via the REST endpoint → FastAPI → same `services.py` function → HANA → response via REST.

**Trade-offs documented**:

| Aspect | REST (Joule Skill) | MCP Tool |
|--------|-------------------|----------|
| Discovery | Manual (upload OpenAPI spec) | Automatic (agent queries `/mcp`) |
| Governance | Tighter — each endpoint registered | Looser — all tools on server available |
| Coupling | Agent knows exact URL + schema | Agent knows only MCP endpoint |
| BTP Property | `sap-joule-studio-action = true` | `sap-joule-studio-mcp-server = true` |
| Best for | Production, governed APIs | Rapid prototyping, multi-agent setups |

**Architectural insight**: The **same service function** serves both paths — proving that the protocol layer (REST vs MCP) is independent of the business logic layer.

---

### Q7. Walk through Scenario 5 (Escalation). How are guardrails enforced at each layer?

**A.** User says: *"Create a ticket."* (no details given)

**Layer 1 — Agent (Joule Studio)**:
- The agent's system prompt says *"never invent data"*.
- It detects missing required parameters (material, plant, priority, team).
- It asks a clarifying question instead of guessing.

**Layer 2 — API (Pydantic)**:
- Even if the agent sent a request with empty fields, Pydantic's `StringConstraints(min_length=1)` would reject it with a 422 Validation Error.

**Layer 3 — Service (RBAC)**:
- If the caller's role is `VIEWER`, the service refuses with HTTP 403 — but still logs a `DENIED` audit row.

**Layer 4 — Database**:
- Even if all above layers failed, HANA column constraints (NOT NULL, max length) would reject bad data.

This demonstrates **defense in depth** — four independent layers of validation.

---

### Q8. What are the three possible `OUTCOME` values in `AUDIT_LOG`, and when does each occur?

**A.**

| Outcome | Trigger Condition | Code Path |
|---------|-------------------|-----------|
| `DENIED` | `role == UserRole.VIEWER` | Checked *before* material validation; audit committed, then `AuthorizationError` raised |
| `FAILURE` | Material not found in HANA, or `dbapi.Error` during insert | Material check fails → audit committed → `ResourceNotFoundError` raised; or DB error → rollback → attempt FAILURE audit → commit |
| `SUCCESS` | Ticket + audit both inserted cleanly | Both inserts succeed → `connection.commit()` commits both atomically |

**Why this matters**: Meena's Rule 2 says *"Every action that writes to HANA must be auditable"* — even failed or denied attempts must be traceable.

---

### Q9. Name all 6 tables in the JOULEOPS schema. Which start empty?

**A.** `MATERIALS`, `CUSTOMERS`, `SALES_ORDERS`, `INVOICES`, `TICKETS`, `AUDIT_LOG`.

`TICKETS` and `AUDIT_LOG` start with 0 rows — they are populated when the agent calls `create_ticket`.

---

### Q10. How many plants does NorthWind have? How many personas? What are their roles?

**A.** 4 plants — Pune (PLT-PUN), Chennai (PLT-CHN), Hyderabad (PLT-HYD), Coimbatore (PLT-CBE).

4 personas:

| Persona | Role | Key Ask |
|---------|------|---------|
| Ramesh | Plant Supervisor (Pune) | Stock check + auto-ticket |
| Priya | Regional Sales Manager (South) | Monday morning open orders report |
| Anil | Finance Controller | Overdue invoice summary + recommendation |
| Meena | IT Architect / Sponsor | Sets the 3 security rules |

---

## Section B — Answers Related to Coding/Configurations [G]

### Q11. Walk me through the exact code path when a VIEWER tries to create a ticket.

**A.** Step-by-step through `services.create_ticket()`:

1. The route handler extracts the `X-User-Role` header and converts it to a `UserRole` enum.
2. `create_ticket()` opens a HANA connection via the context manager.
3. It checks `if role == UserRole.VIEWER` — this check happens **before** any material lookup or ticket insert.
4. If VIEWER, it calls `_insert_audit(cursor, role=role, parameters=parameters, outcome="DENIED")`.
5. Then it calls `connection.commit()` to persist the audit row.
6. Finally, it raises `AuthorizationError("VIEWER is not allowed to create maintenance tickets")` → HTTP 403.
7. The exception propagates to the route, which returns `{"detail": "VIEWER is not allowed..."}`.

**Key insight**: The DENIED audit row is committed *before* the exception is raised — so even unauthorized attempts are logged.

---

### Q12. Why did you set `autocommit=False` in `db.py`? What would break if it were `True`?

**A.** `autocommit=False` means every SQL statement is part of an **explicit transaction** that we control with `connection.commit()` and `connection.rollback()`.

If `autocommit=True`:
- The ticket INSERT would commit **immediately**, even before the audit INSERT.
- If the audit INSERT then fails, we'd have a ticket without an audit trail — violating Meena's Rule 2.
- We could never atomically roll back both operations.

With `autocommit=False`, we call `connection.commit()` only **after** both the ticket and audit rows are inserted — guaranteeing all-or-nothing behavior.

---

### Q13. Why did you force `app.openapi_version = "3.0.3"`? What happens without it?

**A.** FastAPI (built on Starlette + Pydantic v2) generates OpenAPI **3.1.0** by default. However, SAP Build Actions only accepts **3.0.x** specs. Without this override:
- The OpenAPI JSON at `/openapi.json` would use 3.1.0 schema features (like `anyOf`, nullable types).
- When importing into SAP Build Actions, the parser would reject it.
- Joule Studio would not be able to register the skills.

By setting `app.openapi_version = "3.0.3"` in `main.py` (line 25), we force backward-compatible schema output.

---

### Q14. Explain the `_equipment_id()` function. Why does it fall back to a hash?

**A.** The function generates a deterministic equipment ID:
```python
def _equipment_id(material_id: str, plant_code: str) -> str:
    candidate = f"EQ-{plant_code}-{material_id}"
    if len(candidate) <= 30:
        return candidate         # e.g., "EQ-PLT-PUN-MAT-1023"
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:16].upper()
    return f"EQ-{digest}"        # e.g., "EQ-A3F7B2C1D4E5F6A7"
```

**Why the hash fallback?** The `EQUIPMENT_ID` column in HANA has a max length of 30 characters. If the material ID + plant code are long, the naive concatenation would exceed 30 chars and cause a SQL INSERT error. The SHA-256 hash prefix guarantees a fixed-length, collision-resistant alternative.

---

### Q15. Why do you use `SecretStr` instead of a regular `str` for the HANA password?

**A.** `SecretStr` from Pydantic has two protective behaviors:
1. **repr masking** — if the settings object is printed (e.g., in logs, tracebacks), the password shows as `'**********'` instead of the actual value.
2. **Explicit access** — you must call `.get_secret_value()` to get the actual password. This forces intentional access and prevents accidental leaks.

In our `db.py`, line 29: `password=settings.hana_password.get_secret_value()` — this is the only place the real password is ever read.

---

### Q16. How does the `_tool_result()` wrapper in the MCP server enforce source transparency? Show the JSON shape.

**A.** Every MCP tool response is wrapped by `_tool_result()`:

```json
{
  "tool": "get_inventory_snapshot",
  "source_tables": ["MATERIALS"],
  "parameters": {"plant_code": "PLT-CHN"},
  "result": {
    "plant_code": "PLT-CHN",
    "total_materials": 125,
    "total_stock_qty": 45000,
    "inventory_value": 1250000.50,
    "below_safety_stock_count": 12,
    "below_safety_stock_materials": [...],
    "message": "Found 125 materials for plant PLT-CHN."
  }
}
```

The problem statement Section 5F requires that every agent response includes: (1) the tool that was called, (2) the HANA tables, (3) masked parameters. This wrapper provides all three.

---

### Q17. The MCP server imports `from app import services`. Why not duplicate the business logic?

**A.** Code reuse via shared `services.py` provides:
1. **Single source of truth** — one rule engine, one audit logic, one SQL query per operation. If we fix a bug in `summarize_overdue_invoices`, both REST and MCP paths benefit.
2. **Consistent behavior** — the REST endpoint and MCP tool return identical data structures because they call the same function.
3. **DRY principle** — zero duplicated SQL or business rules means lower maintenance overhead.

The MCP server's `server.py` only adds the `_tool_result()` wrapper and `@mcp.tool()` decorator — all heavy lifting is in `services.py`.

---

### Q18. Explain the overdue invoice recommendation rule engine with the exact code conditions.

**A.** The `summarize_overdue_invoices` service in `services.py` applies this decision tree:

```
if overdue_count == 0           → NO_ACTION      ("The customer has no overdue invoices.")
elif oldest_days_overdue > 90   → ESCALATE_TO_LEGAL ("At least one invoice is more than 90 days overdue.")
elif oldest_days >= 60 OR       → HOLD_FURTHER_SHIPMENTS ("The overdue age or credit-limit
     utilization >= 80%                                    utilization requires tighter credit control.")
else                            → SEND_REMINDER  ("The overdue exposure should first receive
                                                    a payment reminder.")
```

**Credit utilization** = `(outstanding_amount / credit_limit) × 100`. If `credit_limit` is 0, utilization defaults to `0.0` to avoid division by zero.

---

### Q19. What is HTTP status code 403 vs 404 vs 503? When does each occur in your project?

**A.**

| Code | Meaning | When It Occurs | Exception Class |
|------|---------|----------------|-----------------|
| **403 Forbidden** | Not authorized | VIEWER role tries to create a ticket | `AuthorizationError` |
| **404 Not Found** | Resource doesn't exist | Material ID not found in HANA | `ResourceNotFoundError` |
| **503 Service Unavailable** | Backend down | HANA Cloud unreachable / query fails | `DatabaseOperationError` |

Each maps to a custom exception class in `services.py` with a `status_code` attribute, caught by FastAPI's `service_error_handler`.

---

### Q20. What is `ConfigDict(extra="forbid")`?

**A.** It tells Pydantic to **reject** any request that includes fields not defined in the model. If someone sends `{"material_id": "MAT-1023", "hack": true}`, Pydantic raises a 422 error. This hardens the API against unexpected payloads.

---

### Q21. What does `strip_whitespace=True` do in `StringConstraints`?

**A.** It automatically removes leading and trailing whitespace from input strings before validation. So `"  MAT-1023  "` becomes `"MAT-1023"`. This prevents issues where a space-padded input wouldn't match the database value.

---

### Q22. What does `separators=(",", ":")` do in `json.dumps()`?

**A.** It removes extra whitespace from the JSON output. Default JSON serialization produces `{"key": "value"}` (with spaces), but with these separators it produces `{"key":"value"}` (compact). This reduces the `PARAMS_MASKED` column size in `AUDIT_LOG`.

---

### Q23. What is Pydantic's `Field(description=...)` used for?

**A.** It adds a description to a model field that appears in the **OpenAPI spec**. For example, `ErrorResponse.detail` has `description="A safe error message without credentials"`. When Joule Studio imports the OpenAPI spec, this description helps the agent understand what each field means.

---

### Q24. How does ngrok work and what is `--host-header=rewrite`?

**A.** **ngrok** creates a secure HTTPS tunnel from a public URL to your local machine:
```bash
ngrok http 8000 --host-header=rewrite
```

- `http 8000` → forward incoming traffic to local port 8000.
- `--host-header=rewrite` → rewrites the incoming `Host` header to `localhost:8000`. Without this, FastAPI might reject the request because the `Host` header would be `xyz.ngrok-free.app` instead of `localhost`.

**Limitation**: Free ngrok supports only 1 tunnel at a time, so we run the FastAPI tunnel and MCP tunnel separately.

---

### Q25. What happens if the ngrok URL changes? How does that affect BTP?

**A.** On the free plan, ngrok generates a **new random URL** every time you restart the tunnel. When this happens:
1. The BTP Destination still points to the old URL.
2. Joule Studio's tool calls will fail with a connection error.
3. You must go to **BTP Cockpit → Connectivity → Destinations** and update the URL.

**In production**, you would deploy to **SAP BTP Cloud Foundry** or **Kyma** with a stable URL.

---

## Section C — Understanding of Basic Concepts [H]

### Q26. What is REST? Why is it the default for Joule Skills?

**A.** **REST** (Representational State Transfer) is an architectural style for web APIs using standard HTTP methods (GET, POST, PUT, DELETE). Resources are identified by URLs and responses are typically JSON.

Joule Skills use REST because:
- It's the **most widely adopted** API style in enterprise software.
- FastAPI generates an **OpenAPI spec** automatically, which Joule Studio can import.
- Each endpoint is **explicitly defined** (URL + method + schema), giving maximum governance.
- SAP Build Actions has first-class support for REST/OpenAPI actions.

---

### Q27. What is an API endpoint? Give an example from your project.

**A.** An API endpoint is a specific URL path that a server exposes to handle requests. Example:

```
GET /materials/MAT-1023/PLT-PUN
```

- **Method**: GET (read-only)
- **Path parameters**: `material_id = "MAT-1023"`, `plant_code = "PLT-PUN"`
- **What it does**: Queries the MATERIALS table and returns stock details as JSON
- **Who uses it**: Ramesh (via Joule Skill `get_material_details`)

---

### Q28. What is a context manager in Python? Where do you use it?

**A.** A context manager is a Python pattern that manages resource setup and teardown using `with` blocks. It guarantees cleanup even if an exception occurs.

In our project, `db.py` uses `@contextmanager` to manage HANA connections:
```python
@contextmanager
def hana_connection() -> Iterator[Any]:
    connection = None
    try:
        connection = dbapi.connect(...)
        yield connection
    except dbapi.Error as error:
        raise DatabaseConnectionError(...) from error
    finally:
        if connection is not None:
            connection.close()   # ← Always closes, even on error
```

Every service function uses it as: `with hana_connection() as connection:` — guaranteeing the connection is closed after use.

---

### Q29. What is an ORM? Why did you NOT use one?

**A.** An **ORM** (Object-Relational Mapper) like SQLAlchemy maps database tables to Python objects, so you write Python code instead of SQL.

We chose **not** to use an ORM because:
1. **SAP HANA specifics** — `hdbcli` is the official SAP-supported driver with full HANA feature support.
2. **Simplicity** — our queries are straightforward (5 endpoints, ~6 queries total).
3. **Performance transparency** — raw parameterized SQL lets us control exactly what executes on HANA.
4. **Security** — parameterized queries (`?` placeholders) prevent SQL injection just as effectively as an ORM.

---

### Q30. What is an enum in Python? Where do you use it?

**A.** An **enum** (enumeration) is a set of named constants that restricts a value to a predefined list. We use `StrEnum` from Python's `enum` module:

```python
class TicketPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class UserRole(StrEnum):
    PLANT_SUPERVISOR = "PLANT_SUPERVISOR"
    SALES_MANAGER = "SALES_MANAGER"
    FINANCE = "FINANCE"
    VIEWER = "VIEWER"
```

**Benefits**:
- Pydantic automatically validates incoming values match the enum — `priority="URGENT"` would be rejected.
- Code uses `UserRole.VIEWER` instead of magic strings, making it typo-proof.
- `StrEnum` (not plain `Enum`) ensures values serialize as strings in JSON responses.

---

### Q31. What is JSON? Why is it used in API responses?

**A.** **JSON** (JavaScript Object Notation) is a lightweight, human-readable data format using key-value pairs and arrays. Example:
```json
{
  "material_id": "MAT-1023",
  "stock_qty": 12,
  "safety_stock": 50,
  "below_safety_stock": true
}
```

It's used because:
- **Language-agnostic** — Joule and our Python server both parse JSON natively.
- **Human-readable** — developers can inspect responses in Swagger UI.
- **LLM-friendly** — the Joule Agent can read JSON to compose natural-language responses.

---

### Q32. What is the `from __future__ import annotations` line at the top of your Python files?

**A.** It enables **PEP 563 postponed evaluation of annotations**, making all type hints strings by default. This allows forward references (using a type before it's defined) and can slightly improve import performance. It's standard practice in modern Python.

---

### Q33. What is `uuid4()` and why do you use it for LOG_ID and TICKET_ID?

**A.** `uuid4()` generates a **random UUID** (Universally Unique Identifier) — a 128-bit value practically guaranteed to be unique without a central authority. We use it because:
- HANA doesn't have an auto-increment like MySQL's `AUTO_INCREMENT`.
- UUIDs are globally unique, so concurrent ticket creation can't collide.
- For TICKET_ID, we take the hex prefix: `TKT-{uuid4().hex[:16].upper()}`.

---

### Q34. What is the difference between `GET` and `POST` in HTTP?

**A.** `GET` is for **reading** data (idempotent, no side effects). `POST` is for **creating** resources (not idempotent, causes state change). In JouleOps, all data-retrieval endpoints use GET; only `create_ticket` uses POST because it writes to the database.

---

### Q35. What is SQL injection? How do you prevent it?

**A.** SQL injection is when an attacker inserts malicious SQL code through user inputs. For example, if we used string concatenation:
```python
# DANGEROUS — never do this!
sql = f"SELECT * FROM MATERIALS WHERE MATERIAL_ID = '{user_input}'"
```
An attacker could input `' OR 1=1 --` to dump the entire table.

We prevent it with **parameterized queries**:
```python
cursor.execute("SELECT * FROM MATERIALS WHERE MATERIAL_ID = ?", (material_id,))
```
The `?` placeholder ensures the value is treated as data, never as SQL code.

---

## Section D — Understanding of Advanced Concepts [I]

### Q36. What is the ReAct pattern? How does the Joule Agent implement it?

**A.** **ReAct** (Reasoning + Acting) is an agentic AI pattern where the agent alternates between:
1. **Reasoning** — thinking about what to do next (which tool to call, with what parameters)
2. **Acting** — executing the chosen tool and observing the result
3. **Repeat** — reason again based on the new observation

In our Joule Agent:
- **Reasoning**: The planner receives the user's query + system prompt → classifies intent → selects tool.
- **Acting**: Joule Studio calls the tool (REST endpoint or MCP) and receives JSON.
- **Repeat**: If the result triggers a follow-up (e.g., stock is low → create ticket), the planner loops back.

This is enabled by the **"planner + tool calling"** toggle in Joule Studio's agent configuration.

---

### Q37. Compare Streamable HTTP vs SSE transport for MCP. Why did you choose Streamable HTTP?

**A.**

| Aspect | SSE (Server-Sent Events) | Streamable HTTP |
|--------|-------------------------|-----------------|
| **Connection** | Long-lived, server pushes events | Standard HTTP request/response |
| **Statefulness** | Stateful — requires persistent connection | Stateless — each request is independent |
| **Tunneling** | Harder through proxies/load balancers | Works through standard HTTP infrastructure |
| **ngrok compatibility** | May have issues with long-lived connections | Works perfectly |
| **Complexity** | Needs event stream parsing | Standard JSON request/response |

We chose **Streamable HTTP** because:
1. It works reliably through **ngrok** tunnels.
2. It's **stateless** (`stateless_http=True`), meaning no session management is needed.
3. It works through **BTP Destinations**, which are standard HTTP proxies.

---

### Q38. What is defense-in-depth? How does your project implement it?

**A.** Defense-in-depth is a security strategy where multiple independent layers of protection guard against failure. In JouleOps:

| Layer | Protection | What It Catches |
|-------|-----------|----------------|
| **1. Agent (Joule Studio)** | System prompt says "never invent data" | Prevents hallucination |
| **2. Pydantic Validation** | `StringConstraints`, enum types, `extra="forbid"` | Rejects malformed or unexpected inputs |
| **3. Service Layer (RBAC)** | `UserRole.VIEWER` check + audit logging | Blocks unauthorized writes |
| **4. SQL Layer** | Parameterized queries (`?` placeholders) | Prevents SQL injection |
| **5. Database** | Column constraints (NOT NULL, max length) | Rejects invalid data at storage level |
| **6. Error Handler** | `ServiceError` → safe JSON response | Prevents credential/SQL leak in responses |

No single layer is the "only" defense — each catches what the previous might miss.

---

### Q39. What are the ACID properties? Which ones does your `create_ticket` function rely on?

**A.** ACID is a set of database transaction properties:

| Property | Meaning | JouleOps Usage |
|----------|---------|----------------|
| **Atomicity** | All or nothing | Ticket + Audit inserts either both commit or both roll back |
| **Consistency** | DB moves from one valid state to another | Column constraints ensure valid ticket data |
| **Isolation** | Concurrent transactions don't interfere | HANA handles this at the DB level |
| **Durability** | Committed data survives crashes | Once `connection.commit()` succeeds, the data is permanent |

Our `create_ticket` most critically relies on **Atomicity** — because `autocommit=False` + explicit `commit()`/`rollback()` ensures the ticket is never created without a matching audit record.

---

### Q40. What is the difference between authentication and authorization? Which does your project implement?

**A.**

| Aspect | Authentication | Authorization |
|--------|---------------|---------------|
| **Question** | *Who are you?* | *What are you allowed to do?* |
| **Mechanism** | Login, tokens, certificates | Roles, permissions, policies |
| **JouleOps** | Not implemented (simulated) | Implemented via `X-User-Role` header |

Our project **simulates** authentication by passing the `X-User-Role` header (the user is trusted to declare their role). In production, SAP BTP would handle authentication via the **XSUAA service** (OAuth 2.0), and the user's role would come from their BTP role collection — not a manually-set header.

We implement **authorization** by checking the role before allowing write operations.

---

### Q41. What would you change for a production deployment?

**A.** Key changes from demo to production:

| Area | Demo (Current) | Production |
|------|---------------|------------|
| **Hosting** | Local + ngrok tunnel | SAP BTP Cloud Foundry or Kyma |
| **Auth** | `X-User-Role` header (simulated) | XSUAA OAuth 2.0 + JWT tokens |
| **RBAC** | Checked in service layer | BTP Role Collections + scope checks |
| **DB connection** | Direct `hdbcli` per request | Connection pooling |
| **Secrets** | `.env` file | SAP BTP Credential Store or K8s Secrets |
| **URL** | Random ngrok URL | Stable CF route or Kyma Ingress |
| **Monitoring** | Print statements | SAP Application Logging Service |
| **Scaling** | Single uvicorn process | Multiple instances behind load balancer |

---

### Q42. Can the Joule Agent call two tools in parallel? Why or why not?

**A.** In the current Joule Studio implementation (GA Jan 2026), the agent executes tools **sequentially**, not in parallel. This is because:

1. **ReAct pattern** — the agent reasons → acts → observes → reasons again. Each "observe" step depends on the previous "act" result.
2. **Conditional logic** — in Scenario 1, the agent must *first* check stock levels *before* deciding whether to create a ticket. Parallel execution would defeat this logic.
3. **Audit trail** — sequential execution makes the trace easier to follow and debug.

However, for independent requests (e.g., "Check stock for MAT-1023 AND show open orders for South"), future agent versions could potentially support parallel tool execution.

---

### Q43. What is hallucination in the context of LLMs? How does JouleOps prevent it?

**A.** **Hallucination** is when an LLM generates information that sounds plausible but is factually wrong — e.g., making up a stock quantity instead of querying the database.

JouleOps prevents hallucination through:
1. **Grounding** — every data point comes from HANA Cloud via tool calls, not from the LLM's training data.
2. **System prompt guardrails** — the instruction says *"never invent data; if a tool returns empty, say 'No records found in HANA Cloud for the given filters'"*.
3. **Source transparency** — the response includes which tool and tables were used, so the user can verify.
4. **No free-form SQL** — the agent can't write arbitrary queries; it can only call predefined tools with specific parameters.

---

### Q44. What is the MCP protocol and how does tool discovery work?

**A.** **MCP (Model Context Protocol)** is an open standard that defines how AI agents discover and invoke external tools. Think of it as a **"USB-C port for AI"**.

**Tool discovery** works like this:
1. The MCP server exposes an endpoint (our `/mcp` on port 8001).
2. When the Joule Agent connects, it sends a discovery request.
3. The MCP server responds with a list of all registered tools, including their names, descriptions, and parameter schemas.
4. The agent stores this tool catalog and can invoke any tool by name.

This is **automatic** — unlike REST/Joule Skills where you must manually upload an OpenAPI spec, MCP tools are discovered dynamically. If you add a new `@mcp.tool()` on the server, the agent picks it up on next connection without any reconfiguration.

---

### Q45. What is a BTP Destination? How does it differ from a simple URL?

**A.** A BTP Destination is more than a URL — it's a **managed, governed connection configuration** that includes:
- The target URL
- Authentication type (NoAuthentication, BasicAuth, OAuth2, etc.)
- Custom properties (like `sap-joule-studio-action = true`)
- Proxy settings, TLS configuration
- Connection pooling and timeout settings

Unlike a simple URL, a Destination is:
- **Centrally managed** in BTP Cockpit
- **Discoverable** by BTP services (Joule Studio reads the properties to find actions/MCP servers)
- **Secure** — credentials are stored in the Destination, not in the calling application

---

## Study Strategy by Parameter

| Parameter | Score Target | Focus Areas | Key Questions |
|-----------|-------------|-------------|---------------|
| **Problem Statement (F)** | Good | Personas, all 5 scenarios, Meena's rules, data flow | Q1–Q10 |
| **Coding/Configurations (G)** | Good | Code walkthroughs, SQL, Pydantic, db.py, MCP server, ngrok | Q11–Q25 |
| **Basic Concepts (H)** | Good | REST, JSON, HTTP, enums, context managers, SQL injection, UUID | Q26–Q35 |
| **Advanced Concepts (I)** | Good | ReAct, ACID, defense-in-depth, MCP vs REST, auth vs authz, hallucination | Q36–Q45 |

> **Scoring reminder**: Good = Clear, accurate, comprehensive. Fair = Adequate with gaps. No Basis = Insufficient.
>
> Master the code paths (Q11, Q12) and architecture (Q36–Q38) — those are where evaluators dig deepest. Good luck! 🚀
