"""Opening, closing and inspecting applications."""

from vani.tools.core import error, quote, resolve_app, run, run_script, tool


@tool
def open_app(app_name: str) -> str:
    """Open (or bring to front) a Mac application by name, e.g. 'Safari', 'chrome', 'spotify'."""
    app = resolve_app(app_name)
    if run(["open", "-a", app]).ok:
        return f"Opened {app}."
    return error(f"could not open '{app_name}'. Is it installed?")


@tool
def quit_app(app_name: str) -> str:
    """Quit an application gracefully by name."""
    app = resolve_app(app_name)
    return run_script(f'tell application "{quote(app)}" to quit').message(f"Quit {app}.")


@tool
def force_quit_app(app_name: str) -> str:
    """Force quit an application that is frozen or not responding."""
    app = resolve_app(app_name)
    if run(["pkill", "-ix", app]).ok:
        return f"Force quit {app}."
    return error(f"{app} does not seem to be running.")


@tool
def list_running_apps() -> str:
    """List the applications that are currently running."""
    res = run_script('tell application "System Events" to get name of '
                     '(processes where background only is false)')
    return res.message(f"Running apps: {res.output}")


@tool
def get_frontmost_app() -> str:
    """Tell which application the user is currently looking at (the active app)."""
    res = run_script('tell application "System Events" to get name of first '
                     'application process whose frontmost is true')
    return res.message(f"The active app is {res.output}.")


@tool
def open_system_settings(pane: str = "") -> str:
    """Open System Settings. pane can be: wifi, bluetooth, sound, display, battery, network, notifications, keyboard, privacy, wallpaper, general. Empty opens the main window."""
    panes = {
        "wifi": "com.apple.wifi-settings-extension",
        "bluetooth": "com.apple.BluetoothSettings",
        "sound": "com.apple.Sound-Settings.extension",
        "display": "com.apple.Displays-Settings.extension",
        "battery": "com.apple.Battery-Settings.extension",
        "network": "com.apple.Network-Settings.extension",
        "notifications": "com.apple.Notifications-Settings.extension",
        "keyboard": "com.apple.Keyboard-Settings.extension",
        "privacy": "com.apple.settings.PrivacySecurity.extension",
        "wallpaper": "com.apple.Wallpaper-Settings.extension",
        "general": "com.apple.systempreferences.GeneralSettings",
    }
    key = pane.lower().strip()
    if key in panes and run(["open", f"x-apple.systempreferences:{panes[key]}"]).ok:
        return f"Opened {key} settings."
    return run(["open", "-a", "System Settings"]).message("Opened System Settings.")
