"""AppleScript helpers. Knows about AppleScript only - nothing about any tool."""

from .runner import CommandResult, run


def quote(text: str) -> str:
    """Escape text for use inside an AppleScript "double quoted" literal."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def _friendly(err: str) -> str:
    if "-1743" in err:
        return ("macOS blocked automation. Allow it in System Settings > "
                "Privacy & Security > Automation.")
    if "-1719" in err or "-25211" in err or "assistive" in err.lower():
        return ("macOS blocked keyboard control. Allow it in System Settings > "
                "Privacy & Security > Accessibility.")
    return err


def run_script(script: str, timeout: int = 30) -> CommandResult:
    res = run(["osascript", "-e", script], timeout)
    return res if res.ok else CommandResult(False, _friendly(res.output))
