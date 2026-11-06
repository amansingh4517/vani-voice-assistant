import os
import wave
import subprocess
from piper.voice import PiperVoice

# --- SINGLETON INSTANCE ---
# Load the 50MB voice model into memory once at startup
print("[SYSTEM] Loading TTS Model...")
MODEL_PATH = "models/amy.onnx"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Did you download it?")

voice = PiperVoice.load(MODEL_PATH)

def speak(text: str):
    """Converts text to speech and plays it through the Mac speakers."""
    
    # Clean the text (remove markdown formatting like **bold** that Piper might try to pronounce)
    clean_text = text.replace('*', '').replace('#', '')
    
    output_file = "output.wav"

    print(f"\n[VOICE DEBUG] 1. Synthesizing audio for: '{clean_text[:20]}...'")

    # 1. Synthesize the audio to a local file
    with wave.open(output_file, 'wb') as wav_file:
        # --- THE FIX: Define the WAV header metadata ---
        wav_file.setnchannels(1)                     # Mono audio
        wav_file.setsampwidth(2)                     # 16-bit audio (2 bytes)
        wav_file.setframerate(voice.config.sample_rate) # Use the Piper model's native sample rate
        
        # Now pour the raw audio data into the file
        voice.synthesize(clean_text, wav_file)
    

    
    print(f"[VOICE DEBUG] 2. Audio file created. Size: {os.path.getsize(output_file)} bytes")
        
    # 2. Ask macOS to play the file natively and block the thread until it finishes
    print("[VOICE DEBUG] 3. Triggering macOS afplay...")
    # This prevents the microphone from turning back on while the speaker is active

    try:
        # capture_output=True forces Python to grab the hidden terminal errors
        result = subprocess.run(["afplay", output_file], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[VOICE ERROR] afplay crashed! Error: {result.stderr}")
        else:
            print("[VOICE DEBUG] 4. Playback complete.")
            
    except Exception as e:
        print(f"[VOICE ERROR] Python failed to run afplay: {str(e)}")

        
    try:
        subprocess.run(["afplay", output_file], check=True)
    except FileNotFoundError:
        print("[ERROR] 'afplay' command not found. Are you on macOS?")
    finally:
        # 3. Clean up the temporary file
        if os.path.exists(output_file):
            os.remove(output_file)