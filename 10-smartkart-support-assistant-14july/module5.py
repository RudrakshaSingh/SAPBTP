"""Module 5 — Bind Tools to the Gemini Model.

THE PROBLEM
-----------
We have defined custom Python tools in Module 4, but the LLM doesn't know they 
exist. If we just ask Gemini "What is the status of ORD-1002?", it will still 
try to guess.

THE SOLUTION
------------
We use `.bind_tools(tools)` to give the LLM a list of functions it is allowed 
to use. 

When the LLM receives a question, it reads the tool descriptions and decides:
1. "Do I need a tool for this?"
2. "If yes, which tool, and what arguments should I pass?"

The LLM does NOT execute the tool. It just returns a `tool_calls` request 
asking US (the Python code) to execute it.

Run:  python module5.py
"""

from module1 import llm
from module4 import (
    calculate_delivery_charge,
    calculate_discount,
    get_estimated_delivery_days,
    get_order_status,
)

# 1. Gather all our tools into a list
tools = [
    get_order_status,
    calculate_discount,
    calculate_delivery_charge,
    get_estimated_delivery_days,
]

# 2. Bind the tools to our Gemini LLM. 
# llm_with_tools is a new runnable that knows about these functions.
llm_with_tools = llm.bind_tools(tools)


if __name__ == "__main__":
    # Let's test the LLM's ability to pick the right tool based on the user's question.
    questions = [
        "What is the status of order ORD-1003?",
        "What will be the final price of ₹10,000 after a 12% discount?",
        "How long does express shipping take?",
        "Thank you for your excellent service.",
    ]

    print("=" * 70)
    print("TESTING TOOL SELECTION")
    print("=" * 70)

    for q in questions:
        print(f"\nUser Question: {q}")
        
        # We invoke the LLM with the bound tools
        response = llm_with_tools.invoke(q)
        
        # Check if the LLM decided to call a tool
        if response.tool_calls:
            print("Gemini Decision: USE A TOOL")
            for tool_call in response.tool_calls:
                print(f"  -> Tool Name: {tool_call['name']}")
                print(f"  -> Arguments: {tool_call['args']}")
        else:
            print("Gemini Decision: NO TOOL REQUIRED (Direct Answer)")
            print(f"  -> Answer: {response.content}")
