import warnings
# Suppress the messy math warnings from the audio models
warnings.filterwarnings("ignore", category=RuntimeWarning)

import queue
import collections
import numpy as np
import sounddevice as sd
from silero_vad_lite import SileroVAD
from mlx_audio.stt import load as load_stt_model
# from config import WAIT_TIME_SECONDS

print("[SYSTEM] Loading Audio Models into Memory...")
vad = SileroVAD(16000)

# Load the MLX Whisper model via mlx-audio (recommended: whisper-large-v3-turbo or base-en)
# This runs directly on your Mac's M-series unified memory via MLX
whisper_model = load_stt_model("mlx-community/whisper-large-v3-turbo-asr-fp16")

def listen_for_command():

    # The thread-safe buffer between the microphone and our AI
    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time, status):
        # Push a copy of the 32ms chunk into the queue
        audio_queue.put(indata.copy())

    audio_buffer = []
    is_speaking = False
    silence_counter = 0
    

    WAIT_TIME_SECONDS = 2.5
    # --- INTERNAL MATH ---
    # We calculate the frames dynamically based on the hardware settings
    CHUNK_SIZE = 512
    SAMPLE_RATE = 16000
    CHUNK_DURATION = CHUNK_SIZE / SAMPLE_RATE  # This equals 0.032 seconds
    
    # Convert seconds into the exact number of frames the loop needs to count
    SILENCE_THRESHOLD = int(WAIT_TIME_SECONDS / CHUNK_DURATION) 

    # --- THE FIX: The Ring Buffer ---
    # Store the last 15 frames (~0.5 seconds) of silence constantly
    pre_speech_buffer = collections.deque(maxlen=15)

    print("\r[EAR] Listening...", end="", flush=True)

    # Start the continuous audio stream (16kHz, mono, 512 frames = 32ms chunks)
    with sd.InputStream(samplerate=16000, channels=1, dtype='float32', 
                        blocksize=512, callback=audio_callback):
        
        # The Main Event Loop
        while True:
            # 1. Grab the next 32ms chunk from the hardware
            chunk = audio_queue.get()[:, 0]
            speech_prob = vad.process(chunk)
            
            # 2. Ask Silero: "Is this a human voice?"
            speech_prob = vad.process(chunk)
            
            if speech_prob > 0.5:
                if not is_speaking:
                    print("\n[Speech Detected] Recording...", end="", flush=True)
                    is_speaking = True

                    # --- THE FIX: Inject the history ---
                    # The moment we detect speech, dump the 0.5 seconds of the past 
                    # into the buffer so we don't lose the first word!
                    for past_chunk in pre_speech_buffer:
                        audio_buffer.extend(past_chunk)
                
                audio_buffer.extend(chunk)
                silence_counter = 0
                
            elif is_speaking:
                # You stopped talking, but we keep buffering just in case you paused for breath
                audio_buffer.extend(chunk)
                silence_counter += 1
                
                # 3. If you remain silent for 1 full second, close the buffer and transcribe
                if silence_counter > SILENCE_THRESHOLD:
                    print("\n[Silence Detected] Transcribing...", flush=True)
                    
                    # Convert the accumulated list into a NumPy array for Whisper
                    audio_data = np.array(audio_buffer, dtype=np.float32)

                    # 1. Clamp values to standard audio ranges (-1.0 to 1.0)
                    audio_data = np.clip(audio_data, -1.0, 1.0)
                    # 2. Replace any NaN or Infinite mathematical errors with 0
                    audio_data = np.nan_to_num(audio_data)

                    # Run STT via mlx-audio generate method
                    # mlx-audio accepts a 1D float32 numpy array directly
                    result = whisper_model.generate(audio_data)
                    text = result.text.strip() if hasattr(result, 'text') else str(result).strip()
                    
                    if text:
                        return text
                    
                    # 4. Reset the state machine for your next sentence
                    is_speaking = False
                    audio_buffer = []
                    silence_counter = 0

            else:
                # --- THE FIX: Maintain the sliding window ---
                # If we are not speaking, keep appending to the ring buffer. 
                # Because maxlen=15, the oldest frame automatically falls off the end.
                pre_speech_buffer.append(chunk)

if __name__ == "__main__":
    listen_for_command()