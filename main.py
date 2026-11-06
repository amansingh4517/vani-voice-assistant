from engine import process_prompt
from tools.ear import listen_for_command
from tools.voice import speak

# Keywords that genuinely mean "quit" — used as a safeguard against
# the LLM incorrectly triggering exit_system on unrelated commands.
EXIT_KEYWORDS = {'exit', 'quit', 'goodbye', 'bye', 'shut down', 'shutdown', 'stop'}

def main():
    # Initialize the system prompt to define the assistant's behavior
    messages = [
        {
            'role': 'system', 
            'content': (
                'You are Andy, a concise personal assistant on macOS. '
                'Keep replies to 1-2 sentences.\n\n'

                'TOOL RULES:\n'
                '- For casual chat, questions, or conversation: just reply normally. DO NOT call any tool.\n'
                '- Only call create_file, read_file, or list_directory when the user explicitly asks to work with files.\n'
                '- NEVER call exit_system unless the user literally says "exit", "quit", "goodbye", or "shut down". '
                'No other phrase should trigger exit_system.\n\n'

                'SAFETY:\n'
                '- Before deleting, overwriting, or moving files, ALWAYS ask for confirmation first.\n'
                '- Before any bulk or recursive operation, ALWAYS ask for confirmation first.\n'
                '- Only proceed after the user explicitly says yes.'
            )
        }
    ]
    
    print("\n=== Voice Agent Initialized ===")
    print("Say 'exit' or 'stop' to quit.\n")
    
    while True:
        user_input = listen_for_command()
        print(f"\n\nYou said: {user_input}")
            
        messages.append({'role': 'user', 'content': user_input})
        
        # Pass the state to the engine and wait for the final text string
        print("[BRAIN] Thinking...")
        assistant_reply = process_prompt(messages)

        if assistant_reply == "EXIT_SIGNAL":
            # Safeguard: only exit if the user actually said an exit keyword.
            # llama3.2 sometimes triggers exit_system incorrectly.
            if any(kw in user_input.lower() for kw in EXIT_KEYWORDS):
                print("Shutting down...")
                speak("Shutting down now. See you later.")
                break
            else:
                # LLM misfired — ignore the false exit and ask the LLM again without tools
                print("[SYSTEM] Ignoring false exit_system trigger.")
                messages.pop()  # remove the user message we just added
                messages.append({'role': 'user', 'content': user_input})
                assistant_reply = process_prompt(messages)
                if assistant_reply == "EXIT_SIGNAL":
                    # Still misfiring, just give a generic reply
                    assistant_reply = "Sorry, I didn't catch that. Could you say that again?"
        
        print(f"\nAssistant: {assistant_reply}\n")
        speak(assistant_reply)

if __name__ == "__main__":
    main()
