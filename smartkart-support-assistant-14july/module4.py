"""Module 4 — Create the Business Tools.

THE PROBLEM
-----------
Language models are very smart, but they do not have access to your private
data (like databases or APIs). If a customer asks "Where is my order?", the
LLM alone can only guess or apologize.

THE SOLUTION
------------
We can create standard Python functions to fetch data from our systems, and
then decorate them with `@tool`. This tells LangChain that these functions
are "tools" that an LLM can choose to run. The docstring of the function is
critical — it is sent to the LLM to explain what the tool does and when to use it.

Run:  python module4.py
"""

from langchain_core.tools import tool

# Tool 1: Order Status Checker
@tool
def get_order_status(order_id: str) -> str:
    """Check the current shipping status of a specific order by its ID.
    
    Args:
        order_id: The unique identifier of the order (e.g., 'ORD-1001').
        
    Returns:
        The current status of the order as a string.
    """
    # A mock database representing what would normally be a SQL/API query
    mock_db = {
        "ORD-1001": "Shipped",
        "ORD-1002": "Processing",
        "ORD-1003": "Delivered",
        "ORD-1004": "Cancelled",
        "ORD-1005": "Out for Delivery",
    }
    
    # We will handle the "Invalid Order ID" exception more gracefully in later modules
    return mock_db.get(order_id, "Order not found")

# Tool 2: Discount Calculator
@tool
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the final price of an item after applying a percentage discount.
    
    Args:
        price: The original price of the product.
        discount_percent: The discount to apply, as a percentage (0-100).
        
    Returns:
        The final discounted price.
    """
    if discount_percent < 0 or discount_percent > 100:
        return "Error: The discount percentage must be between 0 and 100."
    if price < 0:
        return "Error: Price cannot be negative."
        
    return price * (1 - (discount_percent / 100))

# Tool 3: Delivery Charge Calculator
@tool
def calculate_delivery_charge(order_value: float, customer_type: str) -> float:
    """Calculate the delivery fee based on the order value and customer tier.
    
    Args:
        order_value: The total cost of the order.
        customer_type: The tier of the customer ('Premium' or 'Standard').
        
    Returns:
        The delivery charge in currency (₹).
    """
    if customer_type.lower() == "premium":
        return 0.0
    elif customer_type.lower() == "standard" and order_value >= 2000:
        return 0.0
    else:
        return 100.0

# Tool 4: Estimated Delivery Calculator
@tool
def get_estimated_delivery_days(shipping_type: str) -> str:
    """Determine the estimated delivery time frame for a given shipping method.
    
    Args:
        shipping_type: The shipping method chosen ('Standard', 'Express', 'Same Day').
        
    Returns:
        The estimated number of days or timeframe for delivery.
    """
    rules = {
        "standard": "3–5 business days",
        "express": "1–2 business days",
        "same day": "Same day",
    }
    
    # Clean up input string for safer dictionary matching
    key = shipping_type.lower().strip()
    return rules.get(key, "Error: Supported shipping options are Standard, Express, and Same Day.")


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING THE BUSINESS TOOLS LOCALLY")
    print("=" * 70)
    
    # Test get_order_status
    print("\n--- get_order_status ---")
    print(f"Status of ORD-1002: {get_order_status.invoke({'order_id': 'ORD-1002'})}")
    print(f"Status of ORD-9999: {get_order_status.invoke({'order_id': 'ORD-9999'})}")
    
    # Test calculate_discount
    print("\n--- calculate_discount ---")
    print(f"₹5000 with 20% discount: ₹{calculate_discount.invoke({'price': 5000, 'discount_percent': 20})}")
    
    # Test calculate_delivery_charge
    print("\n--- calculate_delivery_charge ---")
    print(f"Standard customer, ₹1500 order: ₹{calculate_delivery_charge.invoke({'order_value': 1500, 'customer_type': 'Standard'})}")
    print(f"Premium customer, ₹500 order: ₹{calculate_delivery_charge.invoke({'order_value': 500, 'customer_type': 'Premium'})}")
    
    # Test get_estimated_delivery_days
    print("\n--- get_estimated_delivery_days ---")
    print(f"Express shipping time: {get_estimated_delivery_days.invoke({'shipping_type': 'Express'})}")

    print("\n" + "=" * 70)
    print("WHY THIS MATTERS — Tools have structured schemas:")
    print("=" * 70)
    # The @tool decorator automatically builds a schema describing the arguments
    # from the python types and docstrings. This schema is what gets sent to Gemini.
    print(get_order_status.name, "schema:")
    print(get_order_status.args_schema.schema_json(indent=2))
