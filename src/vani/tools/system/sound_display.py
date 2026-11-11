"""Speaker volume, screen brightness and appearance."""

from vani.tools.core import error, run_script, tool


@tool
def get_volume() -> str:
    """Get the current output volume (0-100) and whether it is muted."""
    res = run_script("set s to get volume settings\n"
                     'return (output volume of s as string) & "," & (output muted of s as string)')
    if not res.ok:
        return res.message()
    vol, _, muted = res.output.partition(",")
    return f"Volume is {vol}%" + (" and muted." if muted == "true" else ".")


@tool
def set_volume(level: int) -> str:
    """Set the output volume to a level from 0 to 100."""
    level = max(0, min(100, int(level)))
    return run_script(f"set volume output volume {level}").message(f"Volume set to {level}%.")


@tool
def change_volume(amount: int) -> str:
    """Raise or lower the volume by an amount. Positive = louder, negative = quieter. Example: 10 or -10."""
    res = run_script("output volume of (get volume settings)")
    if not res.ok:
        return res.message()
    new = max(0, min(100, int(res.output) + int(amount)))
    return run_script(f"set volume output volume {new}").message(f"Volume is now {new}%.")


@tool
def set_mute(muted: bool) -> str:
    """Mute (true) or unmute (false) the speakers."""
    res = run_script(f"set volume output muted {'true' if muted else 'false'}")
    return res.message("Muted." if muted else "Unmuted.")


@tool
def change_brightness(direction: str, steps: int = 4) -> str:
    """Change screen brightness. direction is 'up' or 'down'. steps is how many key presses (each is about 6%)."""
    code = {"up": 144, "down": 145}.get(direction.lower().strip())
    if code is None:
        return error("direction must be 'up' or 'down'.")
    steps = max(1, min(16, int(steps)))
    script = (f'tell application "System Events"\nrepeat {steps} times\n'
              f'key code {code}\ndelay 0.05\nend repeat\nend tell')
    return run_script(script).message(f"Brightness turned {direction}.")


@tool
def set_dark_mode(enabled: bool) -> str:
    """Turn macOS dark mode on (true) or off (false)."""
    res = run_script('tell application "System Events" to tell appearance preferences '
                     f'to set dark mode to {"true" if enabled else "false"}')
    return res.message(f"Dark mode {'on' if enabled else 'off'}.")


@tool
def toggle_dark_mode() -> str:
    """Switch between dark mode and light mode."""
    res = run_script('tell application "System Events" to tell appearance preferences '
                     'to set dark mode to not dark mode')
    return res.message("Toggled dark mode.")
