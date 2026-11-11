"""Shared building blocks. Tool modules import from here, never from each other."""

from vani.tools.core.app_resolver import resolve_app
from vani.tools.core.applescript import quote, run_script
from vani.tools.core.dates import applescript_date_lines, parse_datetime
from vani.tools.core.paths import human_size, is_protected, resolve_path
from vani.tools.core.registry import registry, tool
from vani.tools.core.results import error, is_error
from vani.tools.core.runner import CommandResult, CommandRunner, get_runner, run, set_runner
from vani.tools.core.safety import is_dangerous_shell

__all__ = [
    "resolve_app", "quote", "run_script", "applescript_date_lines",
    "parse_datetime", "human_size", "is_protected", "resolve_path", "registry",
    "tool", "error", "is_error", "CommandResult", "CommandRunner", "get_runner",
    "run", "set_runner", "is_dangerous_shell",
]
