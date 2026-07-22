"""Module 6 — The Complete Tool-Calling Lifecycle.

THE PROBLEM
-----------
In Module 5, Gemini told us it *wants* to use a tool, but it doesn't actually
run the Python code. We have to do that manually and send the result back.

THE SOLUTION
------------
We will implement the complete loop:
1. Send the user's question to the LLM.
2. The LLM responds with one or more `tool_calls`.
3. We dynamically look up the requested tool from a dictionary (`tool_map`) 
   and execute it with the provided arguments.
4. We wrap the result in a `ToolMessage` (which links the result to the specific 
   tool call ID) and append it to our message history.
5. We send the updated history back to the LLM so it can formulate the final 
   natural-language answer.

This script also handles multiple tool calls natively by looping through 
all requested tools!

Run:  python module6.py
"""

from langchain_core.messages import HumanMessage, ToolMessage

from module5 import llm_with_tools, tools

# Create a dictionary to dynamically map tool names to the actual Python functions.
# This prevents us from having to write massive if/else blocks.
tool_map = {tool.name: tool for tool in tools}

def run_tool_calling_loop(user_query: str) -> str:
    """Executes the full LLM -> Tool -> LLM loop."""
    
    # Step 1: Start the conversation with the user's question
    messages = [HumanMessage(content=user_query)]
    
    print(f"\n[USER] {user_query}")
    
    # Step 2: Get the initial response from the LLM
    ai_response = llm_with_tools.invoke(messages)
    messages.append(ai_response)
    
    # Step 3: Check if Gemini decided a tool was required
    if not ai_response.tool_calls:
        # No tools needed, just return the direct answer
        return ai_response.content
        
    # Step 4-8: The LLM requested tools. We must execute them and return the results.
    print(f"\n[SYSTEM] Gemini requested {len(ai_response.tool_calls)} tool(s). Executing...")
    
    for tool_call in ai_response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]
        
        # Select the actual tool function from our map
        selected_tool = tool_map.get(tool_name)
        
        if selected_tool:
            print(f"  -> Running {tool_name}({tool_args})")
            # Execute the tool
            try:
                raw_result = selected_tool.invoke(tool_args)
            except Exception as e:
                # Basic exception handling for this module
                raw_result = f"Error executing tool: {str(e)}"
        else:
            raw_result = f"Error: Tool '{tool_name}' not found."
            
        print(f"  -> Result: {raw_result}")
        
        # Create a ToolMessage matching the request ID
        tool_message = ToolMessage(
            content=str(raw_result),
            tool_call_id=tool_id
        )
        
        # Append the tool's result to our message history
        messages.append(tool_message)
        
    # Step 9-10: Send the conversation + tool results back to Gemini for the final answer
    print("\n[SYSTEM] Sending tool results back to Gemini...")
    final_response = llm_with_tools.invoke(messages)
    
    return final_response.content


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING TOOL LIFECYCLE & MULTIPLE TOOLS")
    print("=" * 70)
    
    # Test 1: Single tool call
    answer_1 = run_tool_calling_loop("Check the status of ORD-1002.")
    print(f"\n[FINAL ANSWER] {answer_1}")
    
    print("\n" + "=" * 70 + "\n")
    
    # Test 2: Multiple tool calls (Module 9 requirement)
    # The LLM should realize it needs to call BOTH get_order_status AND calculate_discount
    complex_query = (
        "My order ORD-1005 is out for delivery. "
        "I also want to buy another product costing ₹5,000 with a 10% discount. "
        "What is my order status and the discounted product price?"
    )
    answer_2 = run_tool_calling_loop(complex_query)
    print(f"\n[FINAL ANSWER] {answer_2}")
