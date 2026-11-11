"""Keyboard control of the active app (needs Accessibility permission)."""

from vani.tools.core import error, quote, run_script, tool

_KEY_CODES = {"return": 36, "enter": 36, "tab": 48, "space": 49, "delete": 51,
              "escape": 53, "esc": 53, "left": 123, "right": 124, "down": 125, "up": 126}
_MODIFIERS = {"command", "shift", "option", "control"}


@tool
def type_text(text: str) -> str:
    """Type text into whatever app is currently active, as if using the keyboard."""
    return run_script(f'tell application "System Events" to keystroke "{quote(text)}"').message("Typed.")


@tool
def press_keys(key: str, modifiers: str = "") -> str:
    """Press a key or shortcut in the active app. key: a letter/number or return, tab, space, delete, escape, left, right, up, down. modifiers: comma list from command, shift, option, control. Example: key='t', modifiers='command' opens a new tab."""
    mods = [m.strip().lower() for m in modifiers.split(",") if m.strip()]
    if any(m not in _MODIFIERS for m in mods):
        return error("modifiers must be from command, shift, option, control.")
    using = f" using {{{', '.join(m + ' down' for m in mods)}}}" if mods else ""
    k = key.lower().strip()
    action = f"key code {_KEY_CODES[k]}" if k in _KEY_CODES else f'keystroke "{quote(key)}"'
    return run_script(f'tell application "System Events" to {action}{using}').message("Done.")
