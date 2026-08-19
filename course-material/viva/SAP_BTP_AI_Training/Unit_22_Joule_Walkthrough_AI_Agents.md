# 🚀 Unit 22 — Joule Walkthrough & SAP AI Agents

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 34 (8 hours)  
> **Date**: 13-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — Deep Joule Walkthrough

### Q1. Walk through the full Joule experience in SAP S/4HANA step by step.

**A:**

**Scenario: Procurement Manager asking about supplier performance**

```
Environment: SAP S/4HANA Cloud Fiori UI
User: Procurement Manager, role: MM_MANAGER

STEP 1: Access Joule
  → Click the 🤖 Joule icon in Fiori shell header
  → Joule panel slides in from the right side

STEP 2: Enter query
  User types: "Show me supplier performance for our top 5 vendors this quarter"

STEP 3: Intent recognition (milliseconds)
  Joule identifies: supplier_performance_query
  Entities extracted: time_period = "this quarter", limit = 5

STEP 4: Authorization check (silent)
  Joule verifies: User has MM_MANAGER role → can access procurement data

STEP 5: Data retrieval
  Joule calls: MM-API/SupplierPerformance?period=2026Q3&rank=top5
  Returns: [Vendor A: 98.2%, Vendor B: 95.1%, Vendor C: 91.8%, ...]

STEP 6: LLM response generation
  Joule sends to GenAI Hub (GPT-4o):
    - Retrieved data
    - User's question
    - System prompt: "You are a procurement assistant for this user..."

STEP 7: Response displayed in Joule Panel
  ┌──────────────────────────────────────────┐
  │  📊 Top 5 Supplier Performance (Q3 2026) │
  │                                          │
  │  1. Vendor A (TechCorp)      98.2% ✅   │
  │  2. Vendor B (Supplies Inc)  95.1% ✅   │
  │  3. Vendor C (LogiPro)       91.8% ⚠️   │
  │  4. Vendor D (FastShip)      87.3% ❌   │
  │  5. Vendor E (GoodGoods)     84.1% ❌   │
  │                                          │
  │  💡 Vendors D & E are below the 90%     │
  │  threshold. Consider reviewing contracts.│
  │                                          │
  │  [View Details] [Export] [Create Task]   │
  └──────────────────────────────────────────┘

STEP 8: Follow-up action
  User: "Create a review task for Vendor D"
  Joule: [Creates task in S/4HANA] → "Task created and assigned to you."
```

---

### Q2. Walk through Joule in SAP SuccessFactors for HR.

**A:**

```
Scenario: Employee applying for leave

STEP 1: Employee clicks Joule icon in SuccessFactors home page

STEP 2: "I want to take 5 days off next week for a family event"

STEP 3: Joule extracts:
  - Action: apply_leave
  - Duration: 5 days
  - Timing: next week
  - Type: to be confirmed (personal/annual)

STEP 4: Joule checks:
  - Employee's leave balance: Annual = 12 days available ✅
  - Conflicts: No team members on leave that week ✅
  - Approval workflow: Direct manager = Priya Sharma

STEP 5: Joule responds:
  ┌─────────────────────────────────────────────┐
  │ 📅 Leave Request Summary                    │
  │                                             │
  │ Type:       Annual Leave                    │
  │ Dates:      Aug 25-29, 2026 (5 days)        │
  │ Balance:    12 days → 7 days remaining      │
  │ Approver:   Priya Sharma                    │
  │                                             │
  │ Team overlap: None ✅                       │
  │                                             │
  │ [Submit Request] [Change Dates] [Cancel]    │
  └─────────────────────────────────────────────┘

STEP 6: Employee clicks "Submit Request"
  Joule: Submits leave request via SuccessFactors API
  Notification sent to Priya Sharma for approval
  "Your leave request has been submitted. You'll be notified when approved."
```

---

### Q3. How does Joule handle ambiguous queries?

**A:**

```
User: "Show me the report"
           ↓
Joule: Too ambiguous! Which report?
           ↓
Joule asks: "Could you be more specific? Are you looking for:
  1. 📊 Sales Report
  2. 📋 Expense Report
  3. 👥 Headcount Report
  4. Something else?"
           ↓
User: "2"
           ↓
Joule: Retrieves expense reports for this user

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: "What about the policy?"
(In context of HR conversation about leaves)
           ↓
Joule: Uses conversation context
"Referring to the leave policy..." → answers from leave policy docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: "Create a purchase order for 100 units of X from Y for ₹50,000"
           ↓
Joule: Clear intent, but needs confirmation before action:
"I'll create this PO:
  Vendor: Vendor Y
  Material: Product X
  Quantity: 100 units
  Value: ₹50,000
Shall I proceed?"
           ↓
User: "Yes"
Joule: Creates PO in S/4HANA → Returns PO number
```

---

## 🔹 Section 2 — SAP AI Agents

### Q4. What is an SAP AI Agent? How is it different from Joule?

**A:**

| Aspect | SAP Joule | SAP AI Agent |
|--------|----------|--------------|
| **Interaction style** | Conversational, one query at a time | Autonomous, multi-step task execution |
| **Human involvement** | Always present, always confirms | Minimal; acts autonomously (with guardrails) |
| **Goal complexity** | Single action or simple multi-step | Complex, long-horizon goals |
| **Error handling** | Asks user to clarify | Tries alternatives, escalates only when stuck |
| **Tool usage** | Pre-defined SAP APIs | Dynamic tool selection from toolkit |
| **Use case** | Assist individual users | Automate business processes |

**Example contrast:**
```
Joule: "Show me all pending invoices" → User reviews → User clicks "approve 3 of them" → Joule approves

SAP AI Agent: "Process all pending invoices under ₹1 lakh automatically."
  → Agent fetches invoices (tool: get_invoices)
  → Agent validates each against PO (tool: match_po)
  → Agent approves matched ones (tool: approve_invoice)
  → Agent flags mismatches for human review (tool: create_exception)
  → Agent generates summary report (tool: generate_report)
  → All done, no human involvement until exception review
```

---

### Q5. What is the SAP AI Agents framework?

**A:** SAP's AI Agent framework on BTP provides:

| Component | Description |
|-----------|-------------|
| **Tool Library** | Pre-built SAP tools (S/4HANA APIs, SuccessFactors, HANA queries) |
| **Orchestration** | Manages tool-calling LLM loop |
| **Memory** | Task state and context persistence |
| **HITL** | Configurable human approval checkpoints |
| **Audit Trail** | Full log of agent's actions and decisions |
| **Policy Engine** | Rules that restrict what the agent can do |

---

### Q6. What SAP tools are available to AI Agents?

**A:**

**Financial Tools:**
```python
tools = [
    # Accounts Payable
    get_open_invoices(vendor_id, company_code),
    approve_invoice(invoice_id, comment),
    reject_invoice(invoice_id, reason),
    
    # Accounts Receivable
    get_overdue_receivables(customer, aging_bucket),
    send_dunning_notice(customer_id, template),
    
    # General Ledger
    post_journal_entry(debit_account, credit_account, amount, text),
    get_account_balance(account, fiscal_period)
]
```

**Procurement Tools:**
```python
tools = [
    create_purchase_order(vendor, material, quantity, price),
    approve_purchase_requisition(pr_id),
    check_vendor_delivery_status(po_id),
    get_inventory_level(material, plant),
    trigger_goods_receipt(po_id, quantity)
]
```

**HR Tools:**
```python
tools = [
    get_employee_leave_balance(employee_id),
    approve_leave_request(request_id),
    get_headcount_by_department(department),
    create_position(title, department, grade),
    run_payroll_simulation(employee_id, period)
]
```

---

### Q7. Build a complete SAP AP (Accounts Payable) AI Agent with LangGraph.

**A:**

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool
from typing import TypedDict, Annotated
import operator

# Define SAP tools
@tool
def get_pending_invoices(company_code: str, max_amount: float = None) -> list[dict]:
    """Get all pending invoices for a company code. Optionally filter by max amount."""
    query = f"SELECT * FROM BSIK WHERE BUKRS = '{company_code}' AND STATUS = 'PENDING'"
    if max_amount:
        query += f" AND DMBTR <= {max_amount}"
    return hana_conn.execute(query).fetchall()

@tool
def validate_invoice_against_po(invoice_id: str) -> dict:
    """Check if an invoice matches its purchase order. Returns match status and discrepancies."""
    invoice = get_invoice_details(invoice_id)
    po = get_po_details(invoice["po_number"])
    discrepancies = []
    if abs(invoice["amount"] - po["amount"]) > 1.0:
        discrepancies.append(f"Amount mismatch: Invoice ₹{invoice['amount']} vs PO ₹{po['amount']}")
    if invoice["vendor_id"] != po["vendor_id"]:
        discrepancies.append("Vendor mismatch")
    return {"match": len(discrepancies) == 0, "discrepancies": discrepancies}

@tool
def approve_invoice(invoice_id: str, approver_comment: str = "") -> dict:
    """Approve an invoice for payment. Returns approval confirmation."""
    result = s4_api.post(f"/invoices/{invoice_id}/approve",
                          {"comment": approver_comment, "approver": "AI_AGENT"})
    return {"approved": True, "invoice_id": invoice_id, "payment_due": result["payment_due_date"]}

@tool
def flag_for_human_review(invoice_id: str, reason: str) -> dict:
    """Flag an invoice for human review. Creates a work item for AP team."""
    ticket = create_workflow_item(invoice_id, reason, assignee="AP_TEAM")
    return {"flagged": True, "ticket_id": ticket["id"]}

@tool
def generate_processing_summary(processed: list, approved: list, flagged: list) -> str:
    """Generate a summary report of the invoice processing run."""
    return f"""
AP Processing Summary:
  Total processed: {len(processed)}
  Automatically approved: {len(approved)} (₹{sum(a['amount'] for a in approved):,.2f})
  Flagged for review: {len(flagged)}
  Success rate: {len(approved)/len(processed)*100:.1f}%
"""

# State
class APAgentState(TypedDict):
    goal: str
    messages: Annotated[list, operator.add]
    processed_invoices: list
    approved_invoices: list
    flagged_invoices: list
    summary: str

# Create the agent
tools = [get_pending_invoices, validate_invoice_against_po,
         approve_invoice, flag_for_human_review, generate_processing_summary]

llm = init_llm('gpt-4o', temperature=0)
agent_prompt = """You are an Accounts Payable AI agent for Accenture.
Your job is to process pending invoices automatically.
- Auto-approve invoices that exactly match their PO (amount within ₹1 tolerance)
- Flag invoices with discrepancies for human review
- Never approve invoices > ₹5,00,000 (they require human approval regardless)
- Always generate a summary at the end"""

ap_agent = create_react_agent(llm, tools, state_modifier=agent_prompt)

# Run with HITL for invoices > ₹5 lakhs
result = ap_agent.invoke({
    "messages": [{"role": "user", "content":
        "Process all pending invoices for company code 1000 under ₹5 lakhs"}]
})

print(result["messages"][-1].content)
```

---

### Q8. What are the guardrails for SAP AI Agents?

**A:**

| Guardrail | Implementation | Why |
|-----------|---------------|-----|
| **Monetary limits** | Agent cannot approve invoices above threshold | Prevent large unauthorized payments |
| **Action whitelist** | Explicitly list which tools/actions the agent can use | Prevent unexpected side effects |
| **HITL checkpoints** | Pause before irreversible actions | Human confirms before deleting/posting |
| **Audit trail** | Log every action to SAP audit table | Compliance, traceability |
| **Role enforcement** | Agent operates with limited SAP user account | Inherits SAP authorization limits |
| **Rate limits** | Max N actions per run | Prevent runaway processes |
| **Dry-run mode** | Simulate actions without executing | Safe testing |
| **Rollback** | Reverse recent agent actions | Fix mistakes |

---

### Q9. What is the SAP Intelligent Robotic Process Automation (iRPA)?

**A:** **SAP iRPA** is SAP's Robotic Process Automation tool — automating repetitive human tasks in SAP (and non-SAP) systems by mimicking user interactions.

| Aspect | SAP iRPA | SAP AI Agent |
|--------|----------|-------------|
| **Approach** | UI automation (clicks, types in SAP GUI/Fiori) | API-based, intelligent tool-calling |
| **Intelligence** | Rule-based scripts | LLM reasoning, adapts to situations |
| **Flexibility** | Brittle (breaks when UI changes) | Resilient (uses APIs) |
| **Best for** | Structured, predictable repetitive tasks | Variable, judgment-based tasks |
| **Integration** | SAP Build Process Automation | SAP AI Core, LangChain/LangGraph |

**Convergence:** Modern approaches combine both — AI agents for decision-making + iRPA bots for legacy system interactions.

---

## 🔹 Section 3 — End-to-End SAP AI Architecture

### Q10. Draw the complete SAP AI landscape and how all pieces connect.

**A:**

```
BUSINESS USERS
    ↕ (natural language)
SAP JOULE (Copilot Layer)
    ├── Built-in Joule Skills (leave, PO, invoices...)
    └── Custom Joule Skills (Joule Studio)
            ↕ (intents + data)
SAP AI ORCHESTRATION
    ├── Grounding Module → HANA Cloud Vector Engine
    ├── LLM Module      → SAP GenAI Hub
    │                       ├── OpenAI GPT-4o
    │                       ├── Google Gemini
    │                       └── Meta LLaMA
    └── Filter Module   → Azure Content Safety
            ↕
SAP AI CORE (ML Platform)
    ├── Training Jobs (custom ML models)
    ├── Model Deployments (serving endpoints)
    └── Resource Groups (multi-tenancy)
            ↕
SAP DATA LAYER
    ├── HANA Cloud (relational + vector)
    ├── SAP Datasphere (data warehousing)
    └── Object Store (model artifacts, documents)
            ↕
SAP SYSTEMS OF RECORD
    ├── SAP S/4HANA (Finance, Logistics)
    ├── SAP SuccessFactors (HR)
    ├── SAP Ariba (Procurement)
    └── External Systems (via Integration Suite)
```

---

### Q11. What is the difference between a Joule Skill and an SAP AI Agent workflow?

**A:**

| | Joule Skill | SAP AI Agent Workflow |
|-|-------------|----------------------|
| **Triggers** | User message in Joule panel | Scheduled, event-based, or API call |
| **User present** | Always (interactive) | Usually not (background automation) |
| **Duration** | Seconds to minutes | Minutes to hours |
| **Scope** | Single user interaction | Enterprise process automation |
| **Example** | "What's my leave balance?" | "Process all invoices received today" |

---

## 🔹 Section 4 — Quick Fire Questions

### Q12. What is the Joule AI Foundation?

**A:** **Joule AI Foundation** is the underlying AI infrastructure that powers all Joule experiences:
- **LLM access** — Via SAP GenAI Hub (multi-model).
- **Grounding** — Via SAP AI Core Orchestration.
- **Safety** — Content filtering, PII protection.
- **Context** — SAP system context (current user, screen, role).
- **Multi-tenancy** — Each customer's data is isolated.

---

### Q13. What is "responsible AI" in the context of SAP Joule?

**A:** SAP's responsible AI principles in Joule:
- **Transparency** — Always shows which data sources were used.
- **Human control** — Always asks before performing irreversible actions.
- **Compliance** — GDPR data handling, no customer data used for training.
- **Fairness** — No bias in HR-related recommendations.
- **Safety** — Content filtering on all inputs and outputs.

---

### Q14. How does Joule learn from feedback?

**A:** Joule uses feedback loops to improve:
- **Thumbs up/down** on responses → Logged for model fine-tuning.
- **Correction logging** — When users manually correct Joule's work → Used as training signal.
- **Usage analytics** — Track which skills are used most → Prioritize improvements.
- **A/B testing** — Different prompt variations → Track which gives better satisfaction.

Note: SAP does NOT use individual customer data for cross-tenant model training. Feedback improves your organization's Joule instance only, or anonymized for SAP model improvements with consent.

---

### Q15. What is the Joule API vs Joule SDK?

**A:**
- **Joule API** — REST API for programmatically interacting with Joule (send queries, get responses, manage skills).
- **Joule SDK** — JavaScript/TypeScript library for embedding the Joule UI component in your custom web applications.

```javascript
// Joule SDK usage:
import { JouleWidget } from '@sap/joule-ui-widget';

// Embed Joule panel in your custom app
<JouleWidget
  context="CUSTOM_HR_PORTAL"
  initialGreeting="How can I help you with HR queries today?"
  allowedSkills={["HR_Policy_QA", "Leave_Management"]}
  theme="Horizon"
/>
```

---

> **💡 Final Viva Tip:** SAP AI Agents are the most advanced topic. Show the evaluator you understand the END-TO-END flow:
> ```
> Business Problem → SAP AI Agent (LangGraph) → SAP Tools (S/4HANA API) → HANA Data
>                 → GenAI Hub (GPT-4o) → Decision → Action → Audit Log → Summary
> ```
> And connect to your hackathon: "My project was a single-turn RAG; an SAP AI Agent would extend this to multi-step autonomous processing with real SAP system integration."

---

*End of Unit 22 — Joule Walkthrough & SAP AI Agents 🚀*
