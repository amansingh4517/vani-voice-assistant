import ollama
from vani.config import MAIN_MODEL
from vani.tools import ALL_TOOLS, TOOL_MAP
from vani.tools.utility.exit import EXIT_SIGNAL

MAX_STEPS = 6   # stops infinite tool loops


def _run_tool(name: str, arguments: dict) -> str:
    fn = TOOL_MAP.get(name)
    if fn is None:
        return f"Error: unknown tool '{name}'."
    try:
        return str(fn(**arguments))
    except TypeError as e:
        return f"Error: wrong arguments for {name} ({e})."
    except Exception as e:
        return f"Error: {name} failed ({e})."


def process_prompt(messages: list) -> str:
    for _ in range(MAX_STEPS):
        response = ollama.chat(
            model=MAIN_MODEL,
            messages=messages,
            tools=ALL_TOOLS,
            think=True,                       # faster for voice; remove if your ollama version errors
            options={
                "temperature": 0.8,        # Bump this up from 0.4 to 0.8 for creativity
                "top_p": 0.9,              # Keeps word choices natural and prevents wild gibberish
                "repeat_penalty": 1.15     # Prevents loops and repetitive sentence structures
            },
        )
        msg = response.message
        messages.append(msg)

        if not msg.tool_calls:                 # plain answer: done
            return msg.content

        for call in msg.tool_calls:
            name = call.function.name
            print(f"\n[SYSTEM] Executing tool: {name}")
            result = _run_tool(name, call.function.arguments)

            if result == EXIT_SIGNAL:          # never shown to the LLM
                return EXIT_SIGNAL

            messages.append({"role": "tool", "tool_name": name, "content": result})

    return "I got stuck on that one, sir. Could you rephrase it?"