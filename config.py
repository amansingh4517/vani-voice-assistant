MAIN_MODEL = 'qwen3.5:9b'
WAIT_TIME_SECONDS = 1.5        # silence before transcribing (was 2.5)

WAKE_MODEL = 'hey_jarvis'      # openWakeWord pretrained model
WAKE_THRESHOLD = 0.35           # raise if false triggers, lower if it misses you
FOLLOW_UP_SECONDS = 8          # no wake word needed for this long after a reply