"""Shared pytest fixtures for Vani tests."""

import pytest

from vani.tools import set_runner
from vani.tools.core.runner import CommandResult, SubprocessRunner


class FakeRunner:
    """In-memory CommandRunner replacement so tool tests run on any OS."""

    def __init__(self, ok: bool = True, output: str = "") -> None:
        self.ok = ok
        self.output = output
        self.calls: list[list[str]] = []
        self.detached: list[list[str]] = []

    def run(self, args, timeout: int = 30, input_text: str | None = None) -> CommandResult:
        self.calls.append(list(args))
        return CommandResult(self.ok, self.output)

    def spawn_detached(self, args) -> None:
        self.detached.append(list(args))


@pytest.fixture
def fake_runner():
    """Install a FakeRunner for the duration of a test, then restore SubprocessRunner."""
    runner = FakeRunner()
    set_runner(runner)
    try:
        yield runner
    finally:
        set_runner(SubprocessRunner())
