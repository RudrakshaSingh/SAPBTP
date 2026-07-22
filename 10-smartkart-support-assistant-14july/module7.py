"""Module 7 — Add Conversation History.

THE PROBLEM
-----------
In Module 6, every time we called `run_tool_calling_loop()`, we started with a 
brand new list containing only the user's latest question. If the user says 
"What about ORD-1002?" after checking ORD-1003, the LLM has no idea what 
"What about" refers to.

THE SOLUTION
------------
We need to maintain a persistent list of messages (the "conversation history").
Every time the user asks a question, we append it. Every time the LLM answers,
we append it. Every time a tool is called, we append both the request and the 
result.

Run:  python module7.py
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from module5 import llm_with_tools
from module6 import tool_map

def chat_with_history(user_input: str, history: list) -> str:
    """A conversational loop that maintains history across multiple turns."""
    
    # 1. Append the new user question to the existing history
    history.append(HumanMessage(content=user_input))
    
    # 2. Invoke the LLM with the ENTIRE history
    ai_response = llm_with_tools.invoke(history)
    history.append(ai_response)
    
    # 3. If tools are needed, execute them
    if ai_response.tool_calls:
        for tool_call in ai_response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute tool safely
            selected_tool = tool_map.get(tool_name)
            if selected_tool:
                try:
                    result = selected_tool.invoke(tool_args)
                except Exception as e:
                    result = f"Error: {e}"
            else:
                result = "Tool not found."
                
            # Append the tool result to history
            history.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))
            
        # 4. Get the final answer after tool execution
        final_response = llm_with_tools.invoke(history)
        history.append(final_response)
        return final_response.content
        
    # If no tools were needed, just return the direct answer
    return ai_response.content


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING CONVERSATION HISTORY")
    print("=" * 70)
    
    # Initialize an empty history list for this session
    conversation_history = []
    
    # Turn 1
    query_1 = "What is the status of ORD-1003?"
    print(f"\n[USER] {query_1}")
    answer_1 = chat_with_history(query_1, conversation_history)
    print(f"[ASSISTANT] {answer_1}")
    
    # Turn 2: Notice there is no mention of "order status" here!
    # The LLM has to look at the history to understand the context.
    query_2 = "What about ORD-1002?"
    print(f"\n[USER] {query_2}")
    answer_2 = chat_with_history(query_2, conversation_history)
    print(f"[ASSISTANT] {answer_2}")

    print("\n" + "=" * 70)
    print("WHAT DOES THE HISTORY LOOK LIKE?")
    print("=" * 70)
    for msg in conversation_history:
        print(f"[{msg.type.upper()}] {msg.content[:60]}..." if msg.content else f"[{msg.type.upper()}] (Tool Call Request)")
