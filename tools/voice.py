import subprocess
import os
import numpy as np
import soundfile as sf

# --- PRE-FLIGHT: Verify misaki and its dependencies are fully importable ---
# mlx-audio's Kokoro pipeline wraps ImportErrors with a generic message that
# hides the *real* missing package (e.g. num2words, phonemizer).  We surface
# the actual error here so it can be fixed.
_misaki_deps = {"misaki": None, "misaki.en": None, "misaki.espeak": None, "num2words": None}
for _mod_name in _misaki_deps:
    try:
        __import__(_mod_name)
    except ImportError as _exc:
        print(f"[VOICE SETUP ERROR] Cannot import '{_mod_name}': {_exc}")
        print(f"  -> Fix: pip install {_mod_name.split('.')[0]}")
        _misaki_deps[_mod_name] = _exc

# Abort early with an actionable message instead of the misleading Kokoro one.
_failures = {k: v for k, v in _misaki_deps.items() if v is not None}
if _failures:
    _pkgs = sorted({k.split(".")[0] for k in _failures})
    print(f"\n[VOICE SETUP FATAL] Install missing packages:  pip install {' '.join(_pkgs)}")
    print("  Voice synthesis will be disabled until the above packages are installed.\n")

from mlx_audio.tts.utils import load_model

# --- SINGLETON INSTANCE ---
# Loads the model into your M5's Unified Memory once at startup.
print("[SYSTEM] Loading MLX Audio Kokoro Model...")
model = load_model("mlx-community/Kokoro-82M-bf16")

def speak(text: str):
    """Converts text to speech using MLX Audio (Kokoro) and plays it natively."""
    clean_text = text.replace('*', '').replace('#', '').strip()
    if not clean_text:
        return
        
    print(f"\n[VOICE] Synthesizing: {clean_text[:50]}...")
    
    try:
        # 1. Generate the audio using MLX
        # 'af_heart' is a high-quality American Female voice. 
        # You can also try 'am_adam' (American Male) or 'bf_emma' (British Female)
        results = list(model.generate(clean_text, voice="af_heart"))
        
        if not results:
            print("[VOICE ERROR] MLX generated empty audio.")
            return
            
        # 2. Extract the raw audio tensor and convert it to a standard NumPy array
        audio_array = np.array(results[0].audio)
        
        # 3. Save to a temporary WAV file at 24kHz (Kokoro's native sample rate)
        output_file = "output.wav"
        sf.write(output_file, audio_array, 24000)
        
        # 4. Play it using macOS's native blocking audio player
        if os.path.exists(output_file):
            subprocess.run(["afplay", output_file], check=True)
            os.remove(output_file)
            
    except ImportError as e:
        # Surface the *real* missing package — not the generic Kokoro wrapper.
        print(f"[VOICE ERROR] Missing dependency: {e.__cause__ or e}")
    except Exception as e:
        print(f"[VOICE ERROR] MLX Audio failed: {e}")