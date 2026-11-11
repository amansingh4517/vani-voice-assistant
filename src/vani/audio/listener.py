import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import collections
import queue
import time

import numpy as np
import sounddevice as sd
from silero_vad_lite import SileroVAD
from mlx_audio.stt import load as load_stt_model

from vani.config import (WAIT_TIME_SECONDS, WAKE_MODEL, WAKE_THRESHOLD)
from vani.audio.wake import FRAME_SAMPLES, WakeWordDetector

SAMPLE_RATE = 16000
CHUNK_SIZE = 512                               # Silero's 32 ms window
CHUNK_DURATION = CHUNK_SIZE / SAMPLE_RATE
SILENCE_THRESHOLD = int(WAIT_TIME_SECONDS / CHUNK_DURATION)
WAKE_GRACE_SECONDS = 6.0                       # time to start talking after the wake word
WAKE_GAIN = 3.0 

print("[SYSTEM] Loading Audio Models into Memory...")
vad = SileroVAD(SAMPLE_RATE)
whisper_model = load_stt_model("mlx-community/whisper-large-v3-turbo-asr-fp16")
wake = WakeWordDetector(WAKE_MODEL, threshold=WAKE_THRESHOLD, patience=1)

def _transcribe(audio_buffer: list) -> str:
    audio = np.nan_to_num(np.clip(np.array(audio_buffer, dtype=np.float32), -1.0, 1.0))
    result = whisper_model.generate(audio)
    return (result.text if hasattr(result, "text") else str(result)).strip()


def listen_for_command(wait_for_wake: bool = True, timeout: float | None = None) -> str | None:
    """Block until a command is transcribed.

    wait_for_wake=True : stay in cheap wake-word mode until the keyword fires.
    wait_for_wake=False: skip the keyword (follow-up window) and listen right away.
    timeout            : give up and return None if speech doesn't start in time.
    """
    audio_queue: queue.Queue = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        audio_queue.put(indata[:, 0].copy())

    awake = not wait_for_wake
    wake_buf = np.zeros(0, dtype=np.int16)
    pre_speech = collections.deque(maxlen=15)   # ~0.5 s ring buffer
    audio_buffer: list = []
    is_speaking = False
    silence = 0
    deadline = time.monotonic() + timeout if (timeout and awake) else None

    print("\r[EAR] Waiting for wake word..." if not awake else "\r[EAR] Listening...",
          end="", flush=True)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=CHUNK_SIZE, callback=audio_callback):
        while True:
            try:
                chunk = audio_queue.get(timeout=0.25)
            except queue.Empty:
                chunk = None

            if deadline and not is_speaking and time.monotonic() > deadline:
                return None
            if chunk is None:
                continue

            # --- Phase 1: wake word (VAD and Whisper stay idle) ---
            if not awake:
                pcm = np.clip(chunk * WAKE_GAIN, -1.0, 1.0)
                wake_buf = np.concatenate([wake_buf, (pcm * 32767).astype(np.int16)])
                while len(wake_buf) >= FRAME_SAMPLES:
                    frame, wake_buf = wake_buf[:FRAME_SAMPLES], wake_buf[FRAME_SAMPLES:]
                    if wake.process(frame):
                        print("\n[WAKE] Heard you. Listening...", end="", flush=True)
                        awake = True
                        pre_speech.clear()     # keep the wake phrase out of the transcript
                        deadline = time.monotonic() + WAKE_GRACE_SECONDS
                        break
                continue

            # --- Phase 2: your existing VAD -> Whisper pipeline ---
            speech_prob = vad.process(chunk)   # called once per chunk (was twice)

            if speech_prob > 0.5:
                if not is_speaking:
                    print("\n[Speech Detected] Recording...", end="", flush=True)
                    is_speaking = True
                    for past in pre_speech:
                        audio_buffer.extend(past)
                audio_buffer.extend(chunk)
                silence = 0
            elif is_speaking:
                audio_buffer.extend(chunk)
                silence += 1
                if silence > SILENCE_THRESHOLD:
                    print("\n[Silence Detected] Transcribing...", flush=True)
                    text = _transcribe(audio_buffer)
                    if text:
                        return text
                    is_speaking, audio_buffer, silence = False, [], 0
            else:
                pre_speech.append(chunk)