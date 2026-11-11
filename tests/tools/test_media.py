"""Tests for media playback tools."""

from vani.tools import TOOL_MAP


def test_play_song_uses_runner(fake_runner, monkeypatch):
    monkeypatch.setattr(
        "vani.tools.media.media._find_youtube_video",
        lambda query: ("abc123def45", "Shape of You"),
    )
    msg = TOOL_MAP["play_song"]("Shape of You")
    assert "YouTube Music" in msg
    assert len(fake_runner.calls) == 1
    assert fake_runner.calls[0] == ["open", "https://music.youtube.com/watch?v=abc123def45"]
