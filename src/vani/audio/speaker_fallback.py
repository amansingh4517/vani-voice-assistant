import subprocess

def speak(text: str):
    """Converts text to speech and plays it through the Mac speakers using native macOS APIs."""
    
    clean_text = text.replace('*', '').replace('#', '').strip()
    if not clean_text:
        return
        
    print(f"[VOICE] Speaking: {clean_text}")
    
    # We use the built-in macOS 'say' command. 
    # It natively blocks the thread until it finishes talking!
    try:
        subprocess.run(["say", clean_text], check=True)
    except Exception as e:
        print(f"[VOICE ERROR] macOS 'say' command failed: {e}")