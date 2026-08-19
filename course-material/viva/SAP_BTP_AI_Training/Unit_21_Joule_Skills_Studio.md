# 🌟 Unit 21 — Joule Skills with Joule Studio

> **Module**: Module 7 — SAP Business AI  
> **Duration**: Day 33 (8 hours)  
> **Date**: 12-Aug-2026  
> **Stream**: SAP BTP AI Training

---

## 🔹 Section 1 — SAP Joule Overview

### Q1. What is SAP Joule?

**A:** **SAP Joule** is SAP's AI copilot — an embedded, context-aware AI assistant that works across SAP products to help business users accomplish tasks faster through natural language.

**Key characteristics:**

| Characteristic | Description |
|----------------|-------------|
| **Embedded** | Built into SAP S/4HANA, SuccessFactors, Ariba, BTP, etc. — no separate app |
| **Context-aware** | Knows which SAP screen you're on, your role, your data |
| **Action-capable** | Can perform SAP transactions, not just answer questions |
| **Grounded** | Answers from your actual SAP data, not generic knowledge |
| **Role-based** | Respects SAP authorizations — users only see their data |
| **Multi-product** | One Joule experience across the entire SAP portfolio |

**Joule vs ChatGPT:**
- ChatGPT: "How do I create a Purchase Order in SAP?" → Generic instructions.
- Joule: "Create a PO for 100 units of Product X from Vendor Y." → **Actually creates the PO** in your SAP system.

---

### Q2. What can Joule do? Give concrete examples.

**A:**

**In SAP S/4HANA (ERP):**
```
User: "Show me all overdue customer invoices above ₹1 lakh"
Joule: [Queries S/4HANA] → Shows filtered invoice list with aging

User: "Create a goods receipt for purchase order 4500012345"
Joule: [Pre-fills goods receipt form] → "Please review these details and confirm"

User: "What's our inventory level for material MAT-001 in warehouse WH01?"
Joule: [Queries HANA] → "Current stock: 240 units. Reorder point: 200 units."
```

**In SAP SuccessFactors (HR):**
```
User: "Apply for 3 days leave from August 25 to 27"
Joule: [Pre-fills leave request] → "Your leave request for Aug 25-27 is ready. Submit?"

User: "Who are my team members and what are their current tasks?"
Joule: [Queries SuccessFactors] → Shows org chart + task overview

User: "Show me the performance reviews I need to complete by month end"
Joule: [Queries pending reviews] → "You have 4 performance reviews due by Aug 31"
```

**In SAP Ariba (Procurement):**
```
User: "Find me approved suppliers for office stationery under contract"
Joule: → Lists contracted suppliers with pricing

User: "What's the spend with vendor ABC Corp this quarter?"
Joule: → Shows spend analytics
```

---

### Q3. How does Joule work technically?

**A:**

```
User Query: "Show me overdue invoices"
        ↓
1. INTENT RECOGNITION
   Joule classifies: "user wants to query invoice data"
        ↓
2. CONTEXT GATHERING
   Joule knows: user's company code, role, current S/4HANA screen
        ↓
3. ACTION PLANNING
   Joule decides: "Call FI (Finance) invoice API with overdue filter"
        ↓
4. API CALL / DATA RETRIEVAL
   Joule calls S/4HANA API: GET /invoices?status=overdue&user=current_user
        ↓
5. RESPONSE GENERATION (LLM via GenAI Hub)
   "Here are 7 overdue invoices totaling ₹48.2 lakhs..."
        ↓
6. ACTION EXECUTION (if applicable)
   For "create PO" → Pre-fills SAP form, waits for user confirmation
        ↓
7. DISPLAY IN JOULE PANEL
   Structured response with tables, links, and action buttons
```

---

### Q4. What is the Joule Panel?

**A:** The **Joule Panel** is the sidebar UI that appears in SAP Fiori applications. It slides in from the right side and provides:

- **Chat interface** — Ask questions and get responses.
- **Context display** — Shows retrieved data (tables, lists).
- **Quick actions** — Buttons to execute common follow-up actions.
- **Source links** — Links to the actual SAP records referenced.
- **History** — Previous conversation in the session.

Accessible via the 🤖 Joule icon in the Fiori shell header.

---

## 🔹 Section 2 — Joule Studio

### Q5. What is Joule Studio?

**A:** **Joule Studio** is a development environment on SAP BTP for creating **custom Joule Skills** — extending Joule's capabilities for your organization's specific needs.

**What Joule Studio provides:**

| Feature | Description |
|---------|-------------|
| **Skill Editor** | Visual + code editor for creating skills |
| **Intent Designer** | Define what phrases trigger your skill |
| **Data Source Configurator** | Connect to SAP systems, HANA, APIs |
| **Response Template Builder** | Design how Joule displays the answer |
| **Simulator** | Test your skill without deploying |
| **Publishing** | Deploy skill to production Joule |
| **Analytics** | Track skill usage, success rate |

---

### Q6. What is a Joule Skill?

**A:** A **Joule Skill** is a custom capability added to Joule that handles a specific intent or task.

```
Standard Joule (out-of-box):
    ├── Check leave balance
    ├── Create purchase order
    └── View my tasks

Your Custom Skills (added via Joule Studio):
    ├── "IT Equipment Request" skill
    │   → Triggers when: "I need a new laptop/monitor/mouse..."
    │   → Does: Create ServiceNow ticket + notify IT dept
    │
    ├── "Training Enrollment" skill
    │   → Triggers when: "Sign me up for [training name]"
    │   → Does: Check eligibility + enroll in LMS
    │
    └── "HR Policy Q&A" skill (your hackathon use case!)
        → Triggers when: "What is the policy for..."
        → Does: RAG search on HR policy docs via HANA Vector
```

---

### Q7. What are the types of Joule Skills?

**A:**

| Skill Type | What It Does | Example |
|-----------|-------------|---------|
| **Information Retrieval** | Query SAP systems / documents and return data | "Show my leave balance" |
| **Process Automation** | Trigger SAP transactions from natural language | "Create a travel expense report" |
| **Document Q&A** | Answer questions from document knowledge bases (RAG) | "What's our work-from-home policy?" |
| **Guided Action** | Walk user through multi-step process | "Help me complete my year-end review" |
| **Data Entry** | Help fill in forms / data | "Create a new customer record" |

---

### Q8. How do you create a Joule Skill in Joule Studio?

**A:** Skill creation follows these steps:

**Step 1: Define Intent (what phrases trigger the skill)**
```yaml
# Intent definition
skill_name: "HR Policy Q&A"
description: "Answer questions about HR policies, benefits, and procedures"

sample_phrases:
  - "What is the leave policy?"
  - "How many sick days do I get?"
  - "What's the policy for work from home?"
  - "Can I carry forward unused leaves?"
  - "How do I apply for maternity leave?"
  - "What are the rules for business travel?"
  
# Joule uses these samples to train intent classifier
# Phrases can be paraphrased — Joule learns the pattern
```

**Step 2: Define Skill Actions**
```yaml
actions:
  - name: "retrieve_policy"
    type: "document_grounding"
    config:
      data_source: "hana_vector"
      table: "HR_POLICY_CHUNKS"
      embedding_column: "EMBEDDING"
      content_column: "CHUNK_TEXT"
      top_k: 3
      
  - name: "generate_answer"
    type: "llm_generation"
    model: "gpt-4o"
    prompt_template: |
      You are an HR assistant. Answer using ONLY:
      {{retrieved_context}}
      
      Question: {{user_message}}
      If not found, say "This is not covered in available HR policies."
```

**Step 3: Define Response Format**
```yaml
response:
  type: "structured"
  format: |
    **Answer:** {{answer}}
    
    **Source Documents:**
    {{#sources}}
    - {{source_name}} (page {{page}})
    {{/sources}}
    
    *Note: For complex issues, please contact HR directly.*
```

**Step 4: Test in Simulator**
- Enter test phrases → Check intent recognition.
- Check retrieved documents → Verify grounding quality.
- Check LLM response → Verify accuracy and tone.

**Step 5: Publish to Joule**
- Deploy to desired SAP products (S/4HANA, SuccessFactors).
- Set user groups/roles who can access the skill.

---

### Q9. How does intent recognition work in Joule?

**A:** Joule uses a **multi-layer classifier** to determine which skill to invoke:

```
User: "What's the policy for extra leaves during emergencies?"
            ↓
Layer 1: Is this an SAP built-in skill?
  → Check: create_po, check_leave_balance, view_tasks...
  → No match
            ↓
Layer 2: Is this a custom Joule Skill?
  → Check intent vs. all registered custom skills
  → "HR Policy Q&A" skill matches with 92% confidence
            ↓
Layer 3: Extract entities
  → Topic: "emergency leaves", "extra leaves"
  → Pass to skill action as context
            ↓
Invoke: "retrieve_policy" action with extracted topic
```

**Confidence thresholds:**
- > 0.80 → Invoke skill directly.
- 0.60-0.80 → Ask user for clarification ("Did you mean to ask about leave policy?").
- < 0.60 → Joule says it can't help with this.

---

### Q10. What data sources can Joule Skills connect to?

**A:**

| Data Source | Access Method | Example Use |
|-------------|--------------|-------------|
| **SAP S/4HANA** | OData APIs | Query business transactions |
| **SAP SuccessFactors** | SuccessFactors API | HR data, leave balances |
| **SAP HANA Cloud** | SQL + Vector Engine | Custom data, RAG |
| **SAP Ariba** | Ariba API | Procurement data |
| **SharePoint** | Microsoft Graph API | Company documents |
| **ServiceNow** | REST API | IT tickets |
| **Custom REST API** | HTTP connector | Any external system |

---

## 🔹 Section 3 — Advanced Joule Skill Features

### Q11. How do you handle multi-turn conversations in a Joule Skill?

**A:** Joule maintains conversation context across turns within a session:

```
Turn 1: "Show me my leave balance"
Joule: "You have 12 days of annual leave remaining."

Turn 2: "Apply for 3 of those"  ← References previous context
Joule: [Knows "those" = annual leaves] → "Apply for 3 annual leaves. When?"

Turn 3: "Next week, August 25-27"
Joule: [Creates leave request for Aug 25-27] → "Leave request created. Approve?"
```

**Skill configuration for multi-turn:**
```yaml
conversation_context:
  enabled: true
  max_history: 5        # Keep last 5 turns
  entity_tracking:      # Track mentioned entities across turns
    - entity: "leave_type"
    - entity: "date_range"
    - entity: "employee_id"
```

---

### Q12. What are Joule Skill guardrails?

**A:** Skills can have built-in guardrails to prevent misuse:

```yaml
guardrails:
  # Scope limitation
  topic_filter:
    allowed_topics: ["hr_policy", "leave", "benefits", "payroll"]
    rejection_message: "I can only help with HR-related questions."

  # Authorization check
  authorization:
    required_role: "Employee"  # Only logged-in SAP users
    data_scope: "own_data"     # Users can only see their own data

  # Response safety
  content_filter:
    provider: "azure_content_safety"
    threshold: 2

  # Confidence threshold
  intent_confidence_threshold: 0.75  # Don't invoke if less than 75% confident

  # Rate limiting
  rate_limit: "50 requests per user per hour"
```

---

### Q13. How do you test a Joule Skill before publishing?

**A:** Joule Studio provides a **Skill Simulator**:

```
Simulator Test Cases:
  Test 1: "How many leaves can I carry forward?"
    Expected intent: HR_Policy_QA ✅
    Retrieved docs: ["carry_forward_policy.txt", "leave_rules.txt"] ✅
    Answer: "You can carry forward up to 6 unused leave days." ✅

  Test 2: "Book me a flight to Delhi" (out-of-scope)
    Expected intent: NO_MATCH ✅
    Joule response: "I can only help with HR-related questions." ✅

  Test 3: "What is the maternity leave policy?"
    Expected intent: HR_Policy_QA ✅
    Retrieved docs: ["maternity_leave.txt"] ✅
    Answer: "Maternity leave is 26 weeks for the first two children..." ✅
```

**Automated testing:**
```python
# Skill testing via API (before publishing)
from joule_sdk import JouleSkillTester

tester = JouleSkillTester(skill_id="skill-hr-qa-v1")
test_cases = [
    {"input": "How many leaves?", "expected_intent": "HR_Policy_QA"},
    {"input": "Create a PO", "expected_intent": "NO_MATCH"},
]
results = tester.run_test_suite(test_cases)
print(f"Pass rate: {results.pass_rate:.0%}")
```

---

## 🔹 Section 4 — Quick Fire Questions

### Q14. What is the difference between Joule and SAP AI?

**A:**
- **SAP AI** (AI Core, GenAI Hub) — The **infrastructure and platform** layer for AI on BTP. APIs, model deployment, orchestration.
- **Joule** — The **user-facing product** built ON TOP of SAP AI. The copilot experience that business users interact with.

SAP AI is the engine. Joule is the car.

---

### Q15. In which SAP products is Joule available?

**A:**
- SAP S/4HANA Cloud
- SAP SuccessFactors
- SAP Ariba
- SAP Concur
- SAP Customer Experience (CX)
- SAP BTP (developer/admin experience)
- SAP Build (development tools)
- More being added with every quarterly release.

---

### Q16. What language does Joule support?

**A:** Joule supports **multiple languages** based on the underlying LLM capabilities. For enterprise deployments:
- SAP officially supports the major business languages (English, German, French, Spanish, Japanese, Chinese, etc.).
- Language is auto-detected from the user's input.
- Response language matches user's SAP user profile language setting.

---

### Q17. Can Joule access real-time data?

**A:** Yes! This is one of Joule's key advantages over generic AI. Joule calls live SAP APIs at query time — so it always has current data:
- Stock levels from S/4HANA (as of this second, not training time).
- Leave balance from SuccessFactors (updated after last approval).
- Spend data from Ariba (real-time transaction data).

Unlike ChatGPT with a knowledge cutoff, Joule's data is always current.

---

### Q18. What is the Joule API?

**A:** The **Joule API** allows developers to embed Joule capabilities in custom applications:

```javascript
// Embed Joule in a custom Fiori app
import { JouleSDK } from '@sap/joule-sdk';

const joule = new JouleSDK({
    productContext: 'HR_PORTAL',
    userId: currentUser.id,
    tenantId: 'my-tenant'
});

// Open Joule panel with a pre-filled query
joule.openPanel({
    initialMessage: 'Show me my leave balance'
});

// Handle Joule events
joule.on('actionRequested', (action) => {
    if (action.type === 'NAVIGATE') {
        router.navigate(action.target);
    }
});
```

---

> **💡 Viva Tip:** Joule is the "face" of SAP AI for business users. Show you understand the difference between Joule (user-facing copilot) and the underlying AI infrastructure (GenAI Hub, AI Core). The most important concept: Joule Skills extend what Joule can do, and they're built using the same RAG patterns from your hackathon — just packaged for business users.

---

*End of Unit 21 — Joule Skills with Joule Studio 🌟*
