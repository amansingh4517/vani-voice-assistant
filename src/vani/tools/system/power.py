"""Locking, sleeping, restarting and shutting down."""

from vani.tools.core import error, run, run_script, tool


@tool
def lock_screen() -> str:
    """Lock the Mac screen."""
    res = run_script('tell application "System Events" to keystroke "q" '
                     'using {control down, command down}')
    return res.message("Screen locked.")


@tool
def sleep_display() -> str:
    """Turn off the display (the Mac keeps running)."""
    return run(["pmset", "displaysleepnow"]).message("Display off.")


@tool
def sleep_mac() -> str:
    """Put the Mac to sleep."""
    return run_script('tell application "System Events" to sleep').message("Going to sleep.")


@tool
def restart_mac(confirmed: bool = False) -> str:
    """Restart the Mac. Only call with confirmed=true AFTER the user has clearly said yes."""
    if not confirmed:
        return error("not confirmed. Ask the user to confirm before restarting.")
    return run_script('tell application "System Events" to restart').message("Restarting.")


@tool
def shut_down_mac(confirmed: bool = False) -> str:
    """Shut down the Mac. Only call with confirmed=true AFTER the user has clearly said yes."""
    if not confirmed:
        return error("not confirmed. Ask the user to confirm before shutting down.")
    return run_script('tell application "System Events" to shut down').message("Shutting down.")
