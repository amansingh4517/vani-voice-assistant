from engine import process_prompt
from tools.ear import listen_for_command
from tools.voice2 import speak

def main():
    # Initialize the system prompt to define the assistant's behavior
    messages = [
        {
            'role': 'system', 
            'content': (
                'You are Andy, a concise AI assistant on macOS. '
                'Keep verbal replies under 2 sentences. '
                'CRITICAL INSTRUCTION: ONLY use tools if the user explicitly asks you to interact with the file system. '
                'If the user is just chatting, answer conversationally without triggering any tools.'
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
            print("Shutting down...")
            speak("Shutting down now. See you later.")
            break
        
        # 3. THE VOICE: Print the final output (We will add TTS here next)
        print(f"\nAssistant: {assistant_reply}\n")
        speak(assistant_reply) # <-- THE AI SPEAKS ALOUD

if __name__ == "__main__":
    main()