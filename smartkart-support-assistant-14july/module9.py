"""Module 9 — Final End-to-End Test Cases & Capstone.

THE PROBLEM
-----------
We have built a fully functional, robust AI Customer Support Assistant.
Now we need to verify that it meets all business requirements and can handle
complex, multi-part customer queries in a single go.

THE SOLUTION
------------
We run a comprehensive test suite against `customer_support_assistant()`, 
ending with the Capstone Challenge described in the Problem Statement.

Run:  python module9.py
"""

from module8 import customer_support_assistant

def run_test(test_name: str, query: str):
    print("\n" + "-" * 70)
    print(f"TEST: {test_name}")
    print("-" * 70)
    print(f"[USER] {query}")
    
    # We use a fresh history for each test so they don't bleed into each other
    history = []
    answer = customer_support_assistant(query, history)
    
    print(f"[ASSISTANT] {answer}")


if __name__ == "__main__":
    print("=" * 70)
    print("FINAL END-TO-END VERIFICATION")
    print("=" * 70)

    # Test 1: Direct response (No tool required)
    run_test(
        "Direct Response", 
        "Hello, how can you help me?"
    )

    # Test 2: Order lookup (Single tool)
    run_test(
        "Order Lookup", 
        "Check the status of ORD-1001."
    )

    # Test 3: Discount calculation (Single tool, math)
    run_test(
        "Discount Calculation", 
        "A product costs ₹7,500 and has an 18% discount. What is the final price?"
    )

    # Test 4: Delivery calculation (Single tool, conditional logic)
    run_test(
        "Delivery Calculation", 
        "I am a standard customer and my order value is ₹1,800. What is the delivery charge?"
    )

    # Test 5: Structured ticket analysis
    # (Notice how it triggers the [SYSTEM ALERT] background task)
    run_test(
        "Structured Ticket Analysis", 
        "I was charged twice for order ORD-1001 and nobody from support "
        "has responded for three days. Refund my money immediately."
    )

    # Test 6: Multiple tools in one sentence
    run_test(
        "Multiple Tools", 
        "Check ORD-1005 and also tell me the price of a ₹4,000 product after a 25% discount."
    )

    print("\n" + "=" * 70)
    print("CAPSTONE CHALLENGE: SmartKart AI Customer Service Copilot")
    print("=" * 70)
    
    capstone_query = """
    Hello. I ordered a laptop under order ORD-1002.
    Can you check its current status?
    Also, I am thinking of buying headphones worth ₹3,000 with a 15% discount.

    Tell me:
    1. The current status of my laptop order.
    2. The final discounted price of the headphones.
    3. Whether I need to pay a delivery charge as a standard customer.
    """
    
    capstone_history = []
    
    print(f"[USER] {capstone_query.strip()}")
    print("\n[SYSTEM] Assistant is processing... (This may take a moment)")
    
    capstone_answer = customer_support_assistant(capstone_query, capstone_history)
    
    print(f"\n[ASSISTANT] {capstone_answer}")
    
    print("\n" + "=" * 70)
    print("Congratulations! All modules completed successfully.")
    print("=" * 70)
