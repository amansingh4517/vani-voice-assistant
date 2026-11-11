"""Last-resort tools. Prefer a specific tool whenever one exists."""

from .core import error, is_dangerous_shell, run, run_script, tool


@tool
def run_shell_command(command: str, timeout: int = 30) -> str:
    """Run a terminal (zsh) command and return its output. Use only when no other tool fits. Dangerous commands are blocked."""
    if is_dangerous_shell(command):
        return error("that command is blocked for safety.")
    res = run(["/bin/zsh", "-c", f"cd ~ && {command}"], timeout=min(int(timeout), 120))
    text = res.output[:3000] + ("\n[...truncated]" if len(res.output) > 3000 else "")
    return res.message(text or "Done.") if res.ok else error(text or "command failed")


@tool
def run_applescript(script: str) -> str:
    """Run raw AppleScript for anything the other tools cannot do. Use only as a last resort."""
    return run_script(script, timeout=60).message()
