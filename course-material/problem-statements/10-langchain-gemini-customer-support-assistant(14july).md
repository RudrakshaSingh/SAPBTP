# Problem Statement 10 — AI Customer Support & Order Resolution Assistant (LangChain + Google Gemini)

| | |
|---|---|
| **Project Title** | Build an Intelligent Customer Support and Order Resolution Assistant using LangChain, Google Gemini, Pydantic Structured Output, Prompt Templates, Conversation History, and Tool Calling |
| **Domain** | E-commerce Customer Support (company: **SmartKart**) |
| **Topic** | LLM App Development — LangChain, Gemini, LCEL, Pydantic, Tool Calling |
| **Duration** | ~4 Hours |
| **Out of scope** | **RAG is explicitly excluded from this project.** |
| **Implementation** | [`10-smartkart-support-assistant-14july/`](../10-smartkart-support-assistant-14july/) — modules 1–9 map to Modules 1–13 below |

---

## 1. Business Scenario

You work for an e-commerce company named **SmartKart**. Every day, customers contact the support team with questions such as:

- Where is my order?
- I received the wrong product.
- What is the status of order ORD-1002?
- How much will a ₹5,000 product cost after a 15% discount?
- I was charged twice. Please resolve this immediately.
- Can you cancel my order?
- My order has been delayed for seven days.

Currently, support executives manually read each question, identify the type of issue, check internal systems, calculate discounts when required, and decide which support team should handle the request. This process is slow and repetitive.

Your task is to build an **AI Customer Support and Order Resolution Assistant** using:

Google Gemini + LangChain + Prompt Templates + Pydantic Structured Output + Custom Tools + Tool Calling + Conversation History + Exception Handling

The application must understand the customer's question and decide whether to:

- Answer directly, **OR**
- Call an appropriate Python tool, **OR**
- Classify and route the issue to the correct support team

## 2. Final Application Architecture

```
                    CUSTOMER
                       │
                       ▼
              Natural Language Query
                       │
                       ▼
             ┌──────────────────────┐
             │ Google Gemini Model  │
             │ via LangChain        │
             └──────────┬───────────┘
                        │
             Understand user intent
                        │
           ┌────────────┼─────────────┐
           ▼            ▼             ▼
     Direct Answer   Tool Required   Support Issue
                         │              │
                         ▼              ▼
                 Select Python Tool   Pydantic
                         │           Classification
                         ▼              │
                    Execute Tool        ▼
                         │          Structured Output
                         ▼              │
                    ToolMessage         ▼
                         │         Recommended Team
                         ▼
                 Send result to LLM
                         │
                         ▼
                 Natural-Language Answer
                         │
                         ▼
                      CUSTOMER
```

## 3. Learning Objectives

1. Connect Google Gemini with LangChain.
2. Invoke an LLM using `.invoke()`.
3. Create reusable prompts with `ChatPromptTemplate`.
4. Build chains using LCEL and the `|` operator.
5. Use Pydantic `BaseModel`, `Field`, and `Literal`.
6. Generate validated structured output from an LLM.
7. Convert Python functions into AI-callable tools using `@tool`.
8. Bind tools to Gemini using `.bind_tools()`.
9. Understand why an LLM *requests* a tool instead of executing it directly.
10. Execute dynamically selected tools.
11. Return tool results to the LLM through `ToolMessage`.
12. Generate a final natural-language response.
13. Maintain conversation history using `HumanMessage`, `AIMessage`, and `ToolMessage`.
14. Handle invalid inputs, unavailable orders, and execution errors.

## 4. Suggested Time Plan

| Duration | Module | Outcome |
|---|---|---|
| 30 min | Gemini and LangChain setup | Connect and test the model |
| 35 min | Prompt templates and chains | Build reusable prompts |
| 40 min | Structured output using Pydantic | Classify customer issues |
| 50 min | Custom tools | Create business tools |
| 50 min | Tool calling lifecycle | Execute tools and return results |
| 20 min | Conversation history | Build contextual interaction |
| 15 min | Exception handling and testing | Make the application robust |

## 5. Application Requirements

The final assistant must support five major capabilities:

1. Customer-support ticket classification
2. Order-status checking
3. Discount calculation
4. Delivery-charge calculation
5. Conversational follow-up questions

---

## Module 1: Connect LangChain with Google Gemini

Initialize a Google Gemini model using LangChain. The application should accept a simple question:

> Explain customer-support automation in three sentences.

**Expected behavior:** User question → Gemini → Natural-language answer

**Requirements**

- Use `ChatGoogleGenerativeAI`.
- Configure the API key securely — **do not hard-code the API key**.
- Configure an appropriate temperature.
- Successfully invoke the model.

---

## Module 2: Build a Reusable Customer Support Prompt

Create a reusable prompt template that accepts `customer_name`, `customer_query`, `customer_type`.

**Example**

```
Customer name: Rahul
Customer type: Premium
Question: My order has not arrived yet. Please help.
```

The prompt must instruct Gemini to:

1. Understand the customer's issue.
2. Be professional and empathetic.
3. Keep the answer concise.
4. Never invent an order status.
5. Use a tool when real-time order information is required.

**Expected flow:** Dynamic Input → `ChatPromptTemplate` → Gemini → Response

---

## Module 3: Ticket Classification Using Pydantic

Create a Pydantic model called `SupportTicket` with the following fields:

| Field | Allowed values / Description |
|---|---|
| `category` | `Billing`, `Technical`, `Account`, `Delivery`, `Order`, `Refund`, `Other` |
| `priority` | `High`, `Medium`, `Low` |
| `sentiment` | `Positive`, `Neutral`, `Negative` |
| `summary` | A short description of the problem |
| `recommended_team` | The team that should handle the issue |
| `requires_human_agent` | Boolean — `True` / `False` |

### Sample Input 1

> I was charged twice for order ORD-1001. Please refund my money immediately.

**Expected output structure**

```
Category: Billing
Priority: High
Sentiment: Negative
Summary: Customer reports a duplicate charge.
Recommended Team: Billing Support Team
Requires Human Agent: True
```

### Sample Input 2

> I forgot my password and cannot access my account.

**Possible output**

```
Category: Account
Priority: Medium
Sentiment: Neutral
Summary: Customer cannot access the account after forgetting the password.
Recommended Team: Account Support Team
Requires Human Agent: False
```

---

## Module 4: Create the Business Tools

You must create **at least four custom tools**.

### Tool 1: `get_order_status`

**Input:** `order_id`

Use this mock database:

| Order ID | Status |
|---|---|
| ORD-1001 | Shipped |
| ORD-1002 | Processing |
| ORD-1003 | Delivered |
| ORD-1004 | Cancelled |
| ORD-1005 | Out for Delivery |

*Example:* Question "What is the status of ORD-1002?" → `get_order_status(order_id="ORD-1002")` → raw result `Processing` → final answer "Your order ORD-1002 is currently being processed."

### Tool 2: `calculate_discount`

**Inputs:** `price`, `discount_percent`

**Formula:** `Final Price = Price × (1 - Discount Percentage / 100)`

*Example:* ₹5,000 product with 20% discount → ₹4,000

### Tool 3: `calculate_delivery_charge`

**Inputs:** `order_value`, `customer_type`

| Condition | Delivery Charge |
|---|---|
| Premium customer | ₹0 |
| Standard customer and order ≥ ₹2,000 | ₹0 |
| Standard customer and order < ₹2,000 | ₹100 |

*Example:* Standard customer, order value ₹1,500 → ₹100

### Tool 4: `get_estimated_delivery_days`

**Input:** `shipping_type`

| Shipping Type | Delivery Time |
|---|---|
| Standard | 3–5 business days |
| Express | 1–2 business days |
| Same Day | Same day |

---

## Module 5: Bind Tools to the Gemini Model

Provide all four tools to the LLM: `calculate_discount`, `get_order_status`, `calculate_delivery_charge`, `get_estimated_delivery_days`.

The model must intelligently decide which tool is needed:

| Question | Expected model decision |
|---|---|
| What is the status of order ORD-1003? | Call `get_order_status` |
| What will be the final price of ₹10,000 after a 12% discount? | Call `calculate_discount` |
| How long does express shipping take? | Call `get_estimated_delivery_days` |
| Thank you for your excellent service. | No tool required — answer directly |

---

## Module 6: Implement the Complete Tool-Calling Lifecycle

| Step | Action |
|---|---|
| 1 | User sends a question |
| 2 | Gemini analyzes the question |
| 3 | Gemini decides whether a tool is required |
| 4 | If required, Gemini returns: tool name, tool arguments, tool call ID |
| 5 | Python selects the actual tool |
| 6 | Python executes the tool |
| 7 | Tool returns raw result |
| 8 | Create `ToolMessage` |
| 9 | Send conversation + tool result back to Gemini |
| 10 | Gemini generates natural-language final response |

---

## Module 7: Dynamic Tool Selection

Create a dictionary that maps the tool name to the actual tool:

```python
tool_map = {
    "calculate_discount": calculate_discount,
    "get_order_status": get_order_status,
    "calculate_delivery_charge": calculate_delivery_charge,
    "get_estimated_delivery_days": get_estimated_delivery_days
}
```

**Do not hard-code routing like:**

```
If question contains "order":
    call get_order_status
```

Instead, **Gemini** should decide which tool to use based on the natural-language question.

---

## Module 8: Use ToolMessage to Return the Result

Suppose Gemini requests tool `get_order_status` with argument `ORD-1002` and tool call ID `abc123`. Python executes the function and receives `Processing`.

The application must create a `ToolMessage` that conceptually says:

```
The result of tool request abc123 is:
Processing
```

The result is returned to Gemini so it can generate:

> The current status of order ORD-1002 is Processing.

---

## Module 9: Handle Multiple Tool Calls

The application should support a query such as:

> My order ORD-1002 is processing. I also want to buy another product costing ₹5,000 with a 10% discount. What is my order status and the discounted product price?

Gemini may request:

```python
get_order_status(order_id="ORD-1002")      # → Processing
calculate_discount(price=5000, discount_percent=10)   # → 4500
```

**Expected final response:** "Your order ORD-1002 is currently Processing, and the ₹5,000 product will cost ₹4,500 after a 10% discount."

---

## Module 10: Add Conversation History

The assistant must remember previous messages during the current conversation.

```
User:      What is the status of ORD-1003?
Assistant: Order ORD-1003 has been delivered.
User:      What about ORD-1002?
```

The assistant should understand the user is still asking about order status → "Order ORD-1002 is currently Processing."

Use `HumanMessage`, `AIMessage`, `ToolMessage`. The history should look conceptually like:

```
Human: What is the status of ORD-1003?
AI:    I need to check get_order_status.
Tool:  Delivered
AI:    ORD-1003 has been delivered.

Human: What about ORD-1002?
AI:    I need to check get_order_status.
Tool:  Processing
AI:    ORD-1002 is currently Processing.
```

---

## Module 11: Build the Complete Intelligent Assistant

Create a single function conceptually named `customer_support_assistant()` that accepts `user_query` and `conversation_history`.

Flow:

```
Receive query
      ↓
Determine user intent
      ↓
Check whether tool is required
      ↓
Execute one or more tools
      ↓
Return tool results to Gemini
      ↓
Generate final answer
      ↓
Classify support issue when relevant
      ↓
Update conversation history
```

---

## Module 12: Exception Handling

| Case | Input | Expected behavior |
|---|---|---|
| **1. Invalid Order ID** | What is the status of ORD-9999? | Tool returns "Order not found" → "I could not find order ORD-9999. Please verify the order ID and try again." |
| **2. Invalid Discount** | Apply a 150% discount to ₹1,000. | Reject invalid discount → "The discount percentage must be between 0 and 100." |
| **3. Negative Product Price** | Calculate a 10% discount on ₹-500. | Do not calculate; return validation error |
| **4. Unsupported Shipping Type** | How long does super-hyper express delivery take? | "Supported shipping options are Standard, Express, and Same Day." |
| **5. Tool Execution Failure** | Simulate a tool raising an exception | Catch exception → log the error → do not expose technical traceback → "Sorry, I am temporarily unable to retrieve the order status. Please try again later." |

---

## Module 13: Final End-to-End Test Cases

| # | Test Case | Expected |
|---|---|---|
| 1 | **Direct response** — "Hello, how can you help me?" | No tool call; respond directly |
| 2 | **Order lookup** — "Check the status of ORD-1001." | Tool `get_order_status` → `Shipped` |
| 3 | **Discount calculation** — "A product costs ₹7,500 and has an 18% discount. What is the final price?" | ₹6,150 |
| 4 | **Delivery calculation** — "I am a standard customer and my order value is ₹1,800. What is the delivery charge?" | ₹100 |
| 5 | **Structured ticket analysis** — "I was charged twice for order ORD-1001 and nobody from support has responded for three days. Refund my money immediately." | Category: Billing / Priority: High / Sentiment: Negative / Team: Billing Support Team / Requires Human Agent: True |
| 6 | **Multiple tools** — "Check ORD-1005 and also tell me the price of a ₹4,000 product after a 25% discount." | `get_order_status` + `calculate_discount` → "Order ORD-1005 is Out for Delivery, and the discounted product price is ₹3,000." |

---

## Final Capstone Challenge — SmartKart AI Customer Service Copilot

**Customer says:**

> Hello. I ordered a laptop under order ORD-1002. Can you check its current status?
> Also, I am thinking of buying headphones worth ₹3,000 with a 15% discount.
> Tell me:
> 1. The current status of my laptop order.
> 2. The final discounted price of the headphones.
> 3. Whether I need to pay a delivery charge as a standard customer.

The assistant should independently decide it needs three tools:

```python
get_order_status(order_id="ORD-1002")                              # → Processing
calculate_discount(price=3000, discount_percent=15)                # → 2550
calculate_delivery_charge(order_value=2550, customer_type="Standard")  # → 0
```

**Expected final response:**

> Your laptop order ORD-1002 is currently being processed.
> The ₹3,000 headphones will cost ₹2,550 after a 15% discount.
> Since the final order value is above ₹2,000, there is no standard delivery charge.

---

## Student Deliverables

1. A working Jupyter or Google Colab notebook.
2. Secure Gemini API-key configuration.
3. Gemini model initialization.
4. At least one `ChatPromptTemplate`.
5. One Pydantic `BaseModel` for support-ticket classification.
6. At least four custom `@tool` functions.
7. Dynamic tool selection using `bind_tools()`.
8. Manual tool execution.
9. `ToolMessage` integration.
10. Support for multiple tool calls.
11. Conversation history.
12. Exception handling.
13. Execution of all defined test cases.

## Final Workflow to Understand

```
                        User Question
                              │
                              ▼
                         Gemini LLM
                              │
                    Does it need a tool?
                       ↙             ↘
                     No               Yes
                     │                 │
                     ▼                 ▼
              Direct Answer      Select Tool
                                       │
                                       ▼
                                 Execute Python
                                    Function
                                       │
                                       ▼
                                  Tool Result
                                       │
                                       ▼
                                  ToolMessage
                                       │
                                       ▼
                                   Gemini LLM
                                       │
                                       ▼
                              Natural-Language Answer
                                       │
                                       ▼
                            Optional Pydantic Structure
                                       │
                                       ▼
                                  Business Action
```

This project gives an end-to-end understanding of LangChain fundamentals, Gemini integration, prompt templates, LCEL, Pydantic structured output, tool creation, dynamic tool selection, tool execution, `ToolMessage`, conversation history, and exception handling — **all without using RAG**.
