import re                                                    # NEW
from engine import process_prompt
from tools.ear import listen_for_command
from tools.voice import speak
from prompt import build_system_prompt                       # CHANGED (was: system_prompt)

from config import FOLLOW_UP_SECONDS

# Keywords that genuinely mean "quit" — used as a safeguard against
# the LLM incorrectly triggering exit_system on unrelated commands.
QUIT_KEYWORDS = ["exit", "quit", "stop listening", "goodbye", "bye",
                 "go to sleep", "shut down"]                 # NEW
EXACT_QUIT = {"exit", "stop", "quit", "goodbye", "bye"}      # NEW (instant quit, no LLM)


def trim_history(messages, keep_turns=8):                    # NEW (optional)
    """Keep the system prompt + last few user turns, cutting only at a user
    message so a tool call is never separated from its result."""
    role = lambda m: m["role"] if isinstance(m, dict) else m.role
    users = [i for i, m in enumerate(messages) if role(m) == "user"]
    if len(users) <= keep_turns:
        return messages
    return messages[:1] + messages[users[-keep_turns]:]


def main():
    # Initialize the system prompt to define the assistant's behavior
    messages = [
        {
            'role': 'system', 
            'content': build_system_prompt()                 # CHANGED
        }
    ]
    
    print("\n=== Voice Agent Initialized ===")
    print("Say 'exit' or 'stop' to quit.\n")

    follow_up = False
    
    while True:
        user_input = listen_for_command(
            wait_for_wake=not follow_up,
            timeout=FOLLOW_UP_SECONDS if follow_up else None,
        )

        if not user_input or not user_input.strip():  
            follow_up = False          # follow-up window expired -> back to wake word
            continue

        print(f"\n\nYou said: {user_input}")

        if re.sub(r"[^a-z ]", "", user_input.lower()).strip() in EXACT_QUIT:   # NEW
            print("Shutting down...")
            speak("Shutting down now. See you later.")
            break

        messages[0]['content'] = build_system_prompt()       # NEW: fresh date/time each turn
        checkpoint = len(messages)                           # NEW: for rolling back a bad turn
            
        messages.append({'role': 'user', 'content': user_input})
        
        # Pass the state to the engine and wait for the final text string
        print("[BRAIN] Thinking...")
        try:                                                 # NEW
            assistant_reply = process_prompt(messages)
        except Exception as e:                               # NEW
            print(f"[BRAIN] Error: {e}")
            del messages[checkpoint:]
            speak("Sorry, I couldn't reach my brain just now.")
            continue

        if assistant_reply == "EXIT_SIGNAL":
            # NEW: only quit if the user's words actually mean quit
            if not any(re.search(rf"\b{k}\b", user_input.lower()) for k in QUIT_KEYWORDS):
                print("[BRAIN] Ignored a false exit request.")
                del messages[checkpoint:]
                speak("Sorry, I didn't catch that. Could you say it again?")
                continue
            print("Shutting down...")
            speak("Shutting down now. See you later.")
            break

        
        print(f"\nAssistant: {assistant_reply}\n")
        speak(assistant_reply)

        follow_up = True               # next turn needs no wake word for a few seconds
        messages = trim_history(messages)                    # NEW (optional)

if __name__ == "__main__":
    main()