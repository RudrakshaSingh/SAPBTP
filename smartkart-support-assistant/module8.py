"""Module 8 — The Complete Intelligent Assistant & Exception Handling.

THE PROBLEM
-----------
Up until now, our scripts have been somewhat disjointed. We need a single, 
robust entry point that a web frontend or chat UI could call. It needs to:
1. Classify the user's issue (Module 3)
2. Maintain history (Module 10)
3. Call tools dynamically (Modules 6-9)
4. Handle errors gracefully (Module 12) so the user never sees a Python traceback.

THE SOLUTION
------------
We will wrap everything into a `customer_support_assistant(query, history)` 
function. We will also add a `try/except` block around the tool execution so 
that if a tool crashes (e.g., API timeout), the LLM is informed and can 
apologize gracefully.

Run:  python module8.py
"""

from langchain_core.messages import HumanMessage, ToolMessage
import traceback

from module3 import classify_ticket
from module5 import llm_with_tools
from module6 import tool_map

def customer_support_assistant(user_query: str, history: list) -> str:
    """
    The master function for the SmartKart assistant.
    Takes a query and a mutable history list. Updates the list and returns the answer.
    """
    
    # 1. Background Task: Classify the ticket for our internal metrics/routing
    try:
        ticket = classify_ticket(user_query)
        if ticket.requires_human_agent:
            print(f"\n[SYSTEM ALERT] High Priority Issue! Routing to {ticket.recommended_team} in the background.")
    except Exception as e:
        # Don't let a classification failure break the chat experience
        print(f"[SYSTEM ERROR] Classification failed: {e}")
    
    # 2. Append the new message to history
    history.append(HumanMessage(content=user_query))
    
    # 3. Ask the LLM what to do
    try:
        ai_response = llm_with_tools.invoke(history)
        history.append(ai_response)
    except Exception as e:
        return "I am currently experiencing technical difficulties reaching the AI brain. Please try again later."
    
    # 4. Handle tool calls (if any)
    if ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            selected_tool = tool_map.get(tool_name)
            
            # Module 12: Exception Handling
            if selected_tool:
                try:
                    result = selected_tool.invoke(tool_args)
                except Exception as e:
                    # Log the technical error for developers, but send a clean error to the LLM
                    print(f"[DEVELOPER LOG] Tool {tool_name} failed: {traceback.format_exc()}")
                    result = "Error: The system is temporarily unable to process this request."
            else:
                result = f"Error: Tool '{tool_name}' is not recognized by the system."
                
            history.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))
            
        # 5. Get the final natural language answer after tools have run
        try:
            final_response = llm_with_tools.invoke(history)
            history.append(final_response)
            return final_response.content
        except Exception:
            return "I have the information but encountered an error formatting my final answer. Please try again."
            
    # If no tools were needed
    return ai_response.content


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING THE COMPLETE ASSISTANT WITH ERROR HANDLING")
    print("=" * 70)
    
    chat_history = []
    
    # Let's try a query that triggers the classification alert
    query_1 = "I was charged twice for order ORD-1001. Please fix this immediately."
    print(f"\n[USER] {query_1}")
    print(f"[ASSISTANT] {customer_support_assistant(query_1, chat_history)}")
    
    # Let's try a query that triggers an invalid input inside the tool
    query_2 = "Apply a 150% discount to ₹1,000."
    print(f"\n[USER] {query_2}")
    print(f"[ASSISTANT] {customer_support_assistant(query_2, chat_history)}")
