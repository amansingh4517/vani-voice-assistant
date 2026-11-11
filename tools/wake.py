"""Acoustic keyword spotting (wake word), fully on-device via openWakeWord."""

import time

import numpy as np
import openwakeword
from openwakeword.model import Model

FRAME_SAMPLES = 1280  # 80 ms at 16 kHz, int16


class WakeWordDetector:
    def __init__(self, model_name: str, threshold: float = 0.5,
                 patience: int = 2, cooldown_s: float = 1.0) -> None:
        openwakeword.utils.download_models()  # cached after the first run
        self._model = Model(wakeword_models=[model_name], inference_framework="onnx")
        self.threshold, self.patience, self.cooldown_s = threshold, patience, cooldown_s
        self._hits = 0
        self._last = 0.0

    def process(self, frame: np.ndarray) -> bool:
        """Feed one int16 frame of FRAME_SAMPLES. Returns True when the wake word fires."""
        scores = self._model.predict(frame)
        score = max(scores.values(), default=0.0)
        self._hits = self._hits + 1 if score >= self.threshold else 0
        now = time.monotonic()
        if self._hits >= self.patience and now - self._last > self.cooldown_s:
            self._hits, self._last = 0, now
            if hasattr(self._model, "reset"):
                self._model.reset()
            return True
        return False