"""Shared building blocks. Tool modules import from here, never from each other."""

from .app_resolver import resolve_app
from .applescript import quote, run_script
from .dates import applescript_date_lines, parse_datetime
from .paths import human_size, is_protected, resolve_path
from .registry import registry, tool
from .results import error, is_error
from .runner import CommandResult, CommandRunner, get_runner, run, set_runner
from .safety import is_dangerous_shell

__all__ = [
    "resolve_app", "quote", "run_script", "applescript_date_lines",
    "parse_datetime", "human_size", "is_protected", "resolve_path", "registry",
    "tool", "error", "is_error", "CommandResult", "CommandRunner", "get_runner",
    "run", "set_runner", "is_dangerous_shell",
]
