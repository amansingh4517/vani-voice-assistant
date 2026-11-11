# Wake Word Detection

Vani uses **on-device Acoustic Keyword Spotting (KWS)** powered by [`openwakeword`](https://github.com/dscripka/openWakeWord) (`onnxruntime` backend) in `src/vani/audio/wake.py`.

## How It Works

1. **Passive Listening (`wait_for_wake=True`)**
   - `vani.audio.listener` captures 16 kHz mono audio and scales it by `WAKE_GAIN` (`3.0`), accumulating `FRAME_SAMPLES` (`1280` samples = 80 ms) frames for `WakeWordDetector.process(frame)`.
   - While waiting for the wake word, Silero VAD and MLX Whisper remain idle.
2. **Threshold, Patience & Cooldown (`WakeWordDetector`)**
   - `threshold` (`WAKE_THRESHOLD = 0.35`): minimum prediction score to count as a hit.
   - `patience` (`1` in `listener.py`, default `2` on `WakeWordDetector`): number of consecutive frames at or above `threshold` required to trigger.
   - `cooldown_s` (`1.0` s default): minimum seconds after a trigger before firing again; calls `model.reset()` when triggered.
3. **Active Command & Follow-up Window**
   - When the wake word fires, `pre_speech` is cleared (so the wake phrase is excluded from the command transcript), and `listener.py` enters active VAD + Whisper capture with `WAKE_GRACE_SECONDS` (`6.0` s) to begin speaking.
   - After Vani responds in `vani.app`, `follow_up = True` keeps Vani listening for `FOLLOW_UP_SECONDS` (`8` s) without requiring the wake word again—useful for follow-ups and yes/no confirmations. If that window expires with no speech, Vani returns to passive wake-word listening.

## Model Downloads at Runtime

`WakeWordDetector.__init__` calls `openwakeword.utils.download_models()` at runtime. The first run downloads the pretrained ONNX assets and caches them locally; subsequent runs reuse the cached files.

## Tuning & Debugging

Adjust `WAKE_MODEL`, `WAKE_THRESHOLD`, and `FOLLOW_UP_SECONDS` in `src/vani/config.py`.

To test your microphone gain and inspect live confidence scores without launching the full assistant, run:

```bash
python scripts/wake_debug.py
```

Say **"hey jarvis"** and watch the live `score`, `best`, and `mic peak` meter in the terminal.
