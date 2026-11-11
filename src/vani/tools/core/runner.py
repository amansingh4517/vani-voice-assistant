"""Command execution behind an interface (Dependency Inversion principle).

Tools never call subprocess directly. They call run(...), which goes through
a CommandRunner. In production that is SubprocessRunner. In tests, or if you
want logging / dry-run / sandboxing, call set_runner() with another one.
Any class with the same two methods can be swapped in (Liskov principle).
"""

import subprocess
from dataclasses import dataclass
from typing import Optional, Protocol, Sequence

from vani.tools.core.results import error


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    output: str = ""

    def message(self, success: Optional[str] = None) -> str:
        """Turn the result into the string a tool returns."""
        if not self.ok:
            return error(self.output or "command failed")
        if success is not None:
            return success
        return self.output or "Done."


class CommandRunner(Protocol):
    def run(self, args: Sequence[str], timeout: int = 30,
            input_text: Optional[str] = None) -> CommandResult: ...

    def spawn_detached(self, args: Sequence[str]) -> None: ...


class SubprocessRunner:
    """Real implementation: runs commands on this machine (no shell)."""

    def run(self, args: Sequence[str], timeout: int = 30,
            input_text: Optional[str] = None) -> CommandResult:
        try:
            r = subprocess.run(list(args), capture_output=True, text=True,
                               timeout=timeout, input=input_text)
        except FileNotFoundError:
            return CommandResult(False, f"command not found: {args[0]} (this only works on macOS)")
        except subprocess.TimeoutExpired:
            return CommandResult(False, "the action timed out.")
        if r.returncode != 0:
            return CommandResult(False, (r.stderr or r.stdout).strip() or "command failed")
        return CommandResult(True, r.stdout.strip())

    def spawn_detached(self, args: Sequence[str]) -> None:
        subprocess.Popen(list(args), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)


_current: CommandRunner = SubprocessRunner()


def get_runner() -> CommandRunner:
    return _current


def set_runner(runner: CommandRunner) -> None:
    global _current
    _current = runner


def run(args: Sequence[str], timeout: int = 30,
        input_text: Optional[str] = None) -> CommandResult:
    return _current.run(args, timeout, input_text)
