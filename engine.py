import ollama
from tools import TOOL_REGISTRY, AVAILABLE_TOOLS_LIST

def process_prompt(messages: list) -> str:
    """Sends the conversation to the LLM, executes requested tools, and returns the final response."""
    
    # 1. Ask the LLM to route the request
    response = ollama.chat(
        model='llama3.2',
        messages=messages,
        tools=AVAILABLE_TOOLS_LIST
    )

    # 2. Check if tools were requested
    if response.message.tool_calls:
        # Append the LLM's tool request to history
        messages.append(response.message)
        
        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments
            
            print(f"\n[SYSTEM] Executing tool: {tool_name}")
            
            # 3. Route to the correct tool
            if tool_name in TOOL_REGISTRY:
                result = TOOL_REGISTRY[tool_name](**arguments)

                # Intercept the signal immediately. DO NOT feed this back to the LLM.
                if result == "EXIT_SIGNAL":
                    return "EXIT_SIGNAL"
                
                # 4. Feed OS result back to the LLM
                messages.append({
                    'role': 'tool', 
                    'content': result, 
                    'name': tool_name
                })
        
        # 5. Get the final conversational response after tools execute
        final_response = ollama.chat(model='llama3.2', messages=messages)
        messages.append(final_response.message)
        return final_response.message.content
        
    else:
        # No tools needed, just a standard chat response
        messages.append(response.message)
        return response.message.content