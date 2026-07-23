"""Tools the agent can call.

Gemini builds each tool's schema from its signature and docstring, so the
Args/Returns sections below are what the model reads when it decides which
tool to use. Keep them accurate.
"""

from data import COURSES, ORDERS


def search_courses(query: str) -> dict:
    """Search available courses by name, category, or level.

    Args:
        query: Search text such as SAP, beginner, Python, FastAPI, or agentic AI.

    Returns:
        A dictionary containing the number of matches and matching courses.
    """
    query_lower = query.strip().lower()
    matches = [
        course
        for course in COURSES
        if query_lower in course["name"].lower()
        or query_lower in course["category"].lower()
        or query_lower in course["level"].lower()
    ]
    return {"count": len(matches), "courses": matches}


def calculate_discount(course_id: str, discount_percent: float) -> dict:
    """Calculate the final course price after a percentage discount.

    Args:
        course_id: Course identifier such as C101 or C103.
        discount_percent: Discount percentage from 0 through 50.

    Returns:
        Original price, discount amount, and final price in Indian rupees.
    """
    course = next(
        (
            item
            for item in COURSES
            if item["course_id"].upper() == course_id.upper()
        ),
        None,
    )

    if course is None:
        return {"error": f"Course {course_id} was not found."}

    if not 0 <= discount_percent <= 50:
        return {"error": "Discount must be between 0 and 50 percent."}

    original_price = course["price_inr"]
    discount_amount = round(original_price * discount_percent / 100, 2)

    return {
        "course_id": course["course_id"],
        "course_name": course["name"],
        "original_price_inr": original_price,
        "discount_percent": discount_percent,
        "discount_amount_inr": discount_amount,
        "final_price_inr": round(original_price - discount_amount, 2),
    }


def get_order_status(order_id: str) -> dict:
    """Return the status of a course order.

    Args:
        order_id: Order identifier such as ORD-1001.

    Returns:
        Order details or an error when the order is unavailable.
    """
    normalized_order_id = order_id.upper()
    order = ORDERS.get(normalized_order_id)

    if order is None:
        return {"error": f"Order {order_id} was not found."}

    return {"order_id": normalized_order_id, **order}


AGENT_TOOLS = [search_courses, calculate_discount, get_order_status]
