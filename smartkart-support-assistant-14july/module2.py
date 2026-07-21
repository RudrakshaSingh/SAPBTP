"""Module 2 — Build a Reusable Customer Support Prompt.

A ChatPromptTemplate with three variables (customer_name, customer_type,
customer_query), wired into an LCEL chain:  prompt | llm | parser

Run:  python module2.py
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from module1 import llm

# The system message holds the rules that never change; only the human message
# carries the per-request data. That split is what makes the prompt reusable.
SYSTEM_PROMPT = """You are the SmartKart customer support assistant.

Follow these rules on every reply:
1. Understand the customer's underlying issue before answering.
2. Be professional and empathetic. Acknowledge frustration when you see it.
3. Keep the answer concise — 2 to 4 sentences.
4. NEVER invent an order status, refund amount, delivery date, or price.
   If you do not have the real value, say you need to look it up.
5. When real-time order information is required, state that you will use a
   tool to fetch it rather than guessing.

Premium customers get priority handling and free delivery; mention this when
it is relevant."""

HUMAN_PROMPT = """Customer name: {customer_name}
Customer type: {customer_type}
Question:
{customer_query}"""

support_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ]
)

# LCEL: the `|` operator pipes each step's output into the next.
# prompt -> formatted messages -> llm -> AIMessage -> parser -> plain string
support_chain = support_prompt | llm | StrOutputParser()


if __name__ == "__main__":
    # What the template actually produces once the variables are filled in.
    print("=" * 70)
    print("FORMATTED PROMPT")
    print("=" * 70)
    messages = support_prompt.format_messages(
        customer_name="Rahul",
        customer_type="Premium",
        customer_query="My order has not arrived yet. Please help.",
    )
    for m in messages:
        print(f"\n[{m.type.upper()}]\n{m.content}")

    # The same template, reused for different customers.
    cases = [
        {
            "customer_name": "Rahul",
            "customer_type": "Premium",
            "customer_query": "My order has not arrived yet. Please help.",
        },
        {
            "customer_name": "Sneha",
            "customer_type": "Standard",
            "customer_query": "What is the status of order ORD-1002?",
        },
        {
            "customer_name": "Arjun",
            "customer_type": "Standard",
            "customer_query": "Thank you for the quick delivery!",
        },
    ]

    print("\n" + "=" * 70)
    print("CHAIN RESPONSES")
    print("=" * 70)
    for case in cases:
        answer = support_chain.invoke(case)
        print(f"\n--- {case['customer_name']} ({case['customer_type']}) ---")
        print(f"Q: {case['customer_query']}")
        print(f"A: {answer}")
