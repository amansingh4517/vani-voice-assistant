"""Tests for system and advanced macOS tools."""

from tests.conftest import FakeRunner
from vani.tools import TOOL_MAP, set_runner


def test_open_app_uses_runner(fake_runner):
    assert TOOL_MAP["open_app"]("chrome") == "Opened Google Chrome."
    assert fake_runner.calls[0] == ["open", "-a", "Google Chrome"]


def test_failure_becomes_error_string(fake_runner):
    set_runner(FakeRunner(ok=False, output="boom"))
    assert TOOL_MAP["set_volume"](30) == "Error: boom"


def test_confirmation_required_for_shutdown(fake_runner):
    assert TOOL_MAP["shut_down_mac"]().startswith("Error:")
    assert fake_runner.calls == []


def test_shell_blocklist(fake_runner):
    assert TOOL_MAP["run_shell_command"]("sudo ls").startswith("Error:")
    assert fake_runner.calls == []
