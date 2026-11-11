"""Tests for desktop utility tools."""

from vani.tools import TOOL_MAP


def test_timer_spawns_detached(fake_runner):
    assert TOOL_MAP["set_timer"](90, "Tea") == "Timer set for 1 minute and 30 seconds."
    assert len(fake_runner.detached) == 1
