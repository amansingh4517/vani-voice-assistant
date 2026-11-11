"""Small desktop helpers: clipboard, notifications, speech, screenshots, timers."""

import datetime
import os

from .core import error, get_runner, quote, run, run_script, tool


@tool
def get_clipboard() -> str:
    """Read the text currently on the clipboard."""
    res = run(["pbpaste"])
    if not res.ok:
        return res.message()
    return res.output[:3000] if res.output else "The clipboard is empty."


@tool
def set_clipboard(text: str) -> str:
    """Copy text to the clipboard."""
    return run(["pbcopy"], input_text=text).message("Copied to clipboard.")


@tool
def show_notification(title: str, message: str) -> str:
    """Show a macOS notification banner."""
    res = run_script(f'display notification "{quote(message)}" with title "{quote(title)}"')
    return res.message("Notification shown.")


@tool
def speak(text: str, voice: str = "") -> str:
    """Say text out loud using the Mac's built-in voice. voice is optional, e.g. 'Samantha' or 'Daniel'."""
    cmd = ["say"] + (["-v", voice] if voice else []) + [text]
    return run(cmd, timeout=120).message("Spoken.")


@tool
def take_screenshot(interactive: bool = False) -> str:
    """Take a screenshot and save it on the Desktop. Set interactive=true to let the user select an area."""
    stamp = datetime.datetime.now().strftime("%Y-%m-%d at %H.%M.%S")
    dest = os.path.expanduser(f"~/Desktop/Screenshot {stamp}.png")
    res = run(["screencapture", "-i" if interactive else "-x", dest], timeout=60)
    if not res.ok:
        return res.message()
    if os.path.exists(dest):
        return f"Screenshot saved to Desktop as {os.path.basename(dest)}."
    return "Screenshot cancelled."


@tool
def set_timer(seconds: int, label: str = "Timer") -> str:
    """Start a countdown timer. When it ends, a notification shows and the Mac speaks. seconds is the total time in seconds (5 minutes = 300)."""
    seconds = int(seconds)
    if seconds <= 0:
        return error("seconds must be more than zero.")
    script = f'display notification "Time is up." with title "{quote(label)}" sound name "Glass"'
    get_runner().spawn_detached(
        ["/bin/sh", "-c", 'sleep "$0"; osascript -e "$1"; say "$2"',
         str(seconds), script, f"{label} is done."])
    mins, secs = divmod(seconds, 60)
    parts = []
    if mins:
        parts.append(f"{mins} minute{'s' if mins != 1 else ''}")
    if secs:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    return f"Timer set for {' and '.join(parts)}."
