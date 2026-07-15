"""Module 3 — Customer Support Ticket Classification Using Pydantic.

THE PROBLEM
-----------
So far the LLM gives us a paragraph of English. That is fine for a human to
read, but a ticketing system cannot act on a paragraph. It needs fields:
category = "Billing", priority = "High", and so on.

THE SOLUTION
------------
Describe the shape we want as a Pydantic model, then hand that model to the
LLM with `.with_structured_output()`. LangChain converts the model into a
schema, tells Gemini "your answer MUST fit this shape", and parses the reply
back into a real Python object. If Gemini returns something that does not fit,
Pydantic raises an error instead of letting bad data through.

So instead of a string, `.invoke()` now returns a SupportTicket object.

Run:  python module3.py
"""

from typing import Literal

from pydantic import BaseModel, Field

from module1 import llm


class SupportTicket(BaseModel):
    """A customer complaint, turned into structured, machine-readable fields."""

    # Literal = a closed list of allowed values. The LLM is not free to invent
    # a category like "Shipping Problem" — it must pick one of these seven.
    # This is what makes the output safe to feed into a downstream system.
    category: Literal[
        "Billing", "Technical", "Account", "Delivery", "Order", "Refund", "Other"
    ] = Field(description="The type of issue the customer is reporting.")

    priority: Literal["High", "Medium", "Low"] = Field(
        description=(
            "How urgent this is. High = money lost, long delay, or an angry "
            "customer. Low = a simple question."
        )
    )

    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        description="The emotional tone of the customer's message."
    )

    # Free-text fields still get a description. That description is not a
    # comment for us — it is sent to the LLM as the instruction for this field.
    summary: str = Field(
        description="A one-sentence, neutral summary of the customer's problem."
    )

    recommended_team: str = Field(
        description=(
            "The team that should handle this, e.g. 'Billing Support Team', "
            "'Delivery Support Team', 'Account Support Team'."
        )
    )

    requires_human_agent: bool = Field(
        description=(
            "True if a human must step in — refunds, duplicate charges, "
            "angry customers, anything involving money. False if a bot can "
            "resolve it, like a password reset or a status question."
        )
    )


# `.with_structured_output(SupportTicket)` returns a NEW model object that is
# locked to this schema. Calling .invoke() on it gives back a SupportTicket
# instance, NOT an AIMessage. There is no .content and no .text to unwrap.
ticket_classifier = llm.with_structured_output(SupportTicket)


def classify_ticket(customer_message: str) -> SupportTicket:
    """Turn a raw customer message into a structured SupportTicket."""
    return ticket_classifier.invoke(
        "Classify this SmartKart customer support message:\n\n" + customer_message
    )


def print_ticket(message: str, ticket: SupportTicket) -> None:
    """Pretty-print one classification result."""
    print("\n" + "-" * 70)
    print("CUSTOMER SAID:")
    print("  " + message.strip().replace("\n", "\n  "))
    print("\nCLASSIFIED AS:")
    print(f"  Category:             {ticket.category}")
    print(f"  Priority:             {ticket.priority}")
    print(f"  Sentiment:            {ticket.sentiment}")
    print(f"  Summary:              {ticket.summary}")
    print(f"  Recommended Team:     {ticket.recommended_team}")
    print(f"  Requires Human Agent: {ticket.requires_human_agent}")


if __name__ == "__main__":
    samples = [
        # Sample 1 from the problem statement -> expect Billing / High / Negative
        "I was charged twice for order ORD-1001. Please refund my money immediately.",
        # Sample 2 -> expect Account / Medium / Neutral
        "I forgot my password and cannot access my account.",
        # Test Case 5 -> expect Billing / High / Negative / human agent = True
        "I was charged twice for order ORD-1001 and nobody from support "
        "has responded for three days. Refund my money immediately.",
    ]

    for message in samples:
        print_ticket(message, classify_ticket(message))

    # The result is a real Pydantic object, so we get all the usual benefits:
    # attribute access, and free conversion to a dict or JSON for an API or
    # a database row.
    print("\n" + "=" * 70)
    print("WHY THIS MATTERS — the result is an object, not text:")
    print("=" * 70)
    ticket = classify_ticket(samples[0])
    print("Attribute access:", ticket.priority, "->", type(ticket.priority).__name__)
    print("Route the ticket: send to", ticket.recommended_team)
    print("Escalate?        ", "YES" if ticket.requires_human_agent else "no")
    print("\nAs JSON, ready for a database or an API:")
    print(ticket.model_dump_json(indent=2))
