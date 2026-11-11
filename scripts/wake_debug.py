import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model
from vani.config import WAKE_MODEL

openwakeword.utils.download_models()
model = Model(wakeword_models=[WAKE_MODEL], inference_framework="onnx")

FRAME = 1280
best = 0.0
print("Say 'hey jarvis'. Ctrl+C to stop.\n")

with sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=FRAME) as stream:
    while True:
        data, _ = stream.read(FRAME)
        frame = data[:, 0]
        score = max(model.predict(frame).values(), default=0.0)
        peak = int(np.abs(frame).max())
        best = max(best, score)
        bar = "#" * int(score * 40)
        print(f"\rscore {score:.2f} | best {best:.2f} | mic peak {peak:5d} | {bar:<40}", end="", flush=True)