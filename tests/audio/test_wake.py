"""Tests for WakeWordDetector threshold, patience, and cooldown behavior."""

import numpy as np

from vani.audio import wake as wake_mod


class _FakeClock:
    def __init__(self, start: float = 100.0) -> None:
        self.now = start

    def monotonic(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class _FakeOWWModel:
    def __init__(self, scores: list[float]) -> None:
        self._scores = iter(scores)
        self.reset_calls = 0

    def predict(self, frame: np.ndarray) -> dict[str, float]:
        return {"hey_jarvis": next(self._scores, 0.0)}

    def reset(self) -> None:
        self.reset_calls += 1


def _make_detector(monkeypatch, scores: list[float], **kwargs):
    clock = _FakeClock()
    fake_model = _FakeOWWModel(scores)
    downloads: list[bool] = []

    monkeypatch.setattr(wake_mod.openwakeword.utils, "download_models", lambda: downloads.append(True))
    monkeypatch.setattr(wake_mod, "Model", lambda **kw: fake_model)
    monkeypatch.setattr(wake_mod.time, "monotonic", clock.monotonic)

    detector = wake_mod.WakeWordDetector("hey_jarvis", **kwargs)
    return detector, fake_model, clock, downloads


def test_threshold_triggers_when_patience_is_one(monkeypatch):
    frame = np.zeros(wake_mod.FRAME_SAMPLES, dtype=np.int16)
    detector, fake_model, _, downloads = _make_detector(
        monkeypatch, [0.10, 0.34, 0.35], threshold=0.35, patience=1, cooldown_s=1.0
    )

    assert downloads == [True]
    assert detector.process(frame) is False
    assert detector.process(frame) is False
    assert detector.process(frame) is True
    assert fake_model.reset_calls == 1


def test_patience_requires_consecutive_hits(monkeypatch):
    frame = np.zeros(wake_mod.FRAME_SAMPLES, dtype=np.int16)
    # Hit, miss (resets counter), hit, hit -> fires on 4th frame
    detector, fake_model, _, _ = _make_detector(
        monkeypatch, [0.8, 0.2, 0.6, 0.7], threshold=0.5, patience=2, cooldown_s=1.0
    )

    assert detector.process(frame) is False
    assert detector.process(frame) is False
    assert detector.process(frame) is False
    assert detector.process(frame) is True
    assert fake_model.reset_calls == 1


def test_cooldown_suppresses_immediate_retrigger(monkeypatch):
    frame = np.zeros(wake_mod.FRAME_SAMPLES, dtype=np.int16)
    detector, fake_model, clock, _ = _make_detector(
        monkeypatch, [0.9, 0.9, 0.9, 0.9], threshold=0.5, patience=1, cooldown_s=1.5
    )

    assert detector.process(frame) is True
    clock.advance(0.5)
    assert detector.process(frame) is False
    clock.advance(0.9)  # total 1.4s <= 1.5s
    assert detector.process(frame) is False
    clock.advance(0.2)  # total 1.6s > 1.5s
    assert detector.process(frame) is True
    assert fake_model.reset_calls == 2
