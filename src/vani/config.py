MAIN_MODEL = "qwen3.5:9b"
LLM_TEMPERATURE = 0.8
LLM_TOP_P = 0.9
LLM_REPEAT_PENALTY = 1.15

WAIT_TIME_SECONDS = 1.5        # silence before transcribing (was 2.5)

WAKE_MODEL = "hey_jarvis"      # openWakeWord pretrained model
WAKE_THRESHOLD = 0.35          # raise if false triggers, lower if it misses you
FOLLOW_UP_SECONDS = 8          # no wake word needed for this long after a reply

TTS_MODEL = "mlx-community/Kokoro-82M-bf16"
TTS_VOICE = "hf_alpha"
TTS_LANG_CODE = "h"
TTS_SPEED = 1.0
