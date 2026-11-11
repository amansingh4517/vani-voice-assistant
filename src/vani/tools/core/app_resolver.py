"""Turns a spoken app name ('chrome', 'vs code') into the real app name."""

import os

APP_ALIASES = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "code": "Visual Studio Code",
    "settings": "System Settings",
    "system preferences": "System Settings",
    "preferences": "System Settings",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "teams": "Microsoft Teams",
    "iterm": "iTerm",
}

APP_FOLDERS = ["/Applications", "/System/Applications",
               "/System/Applications/Utilities", "/Applications/Utilities",
               os.path.expanduser("~/Applications")]


def _installed_apps() -> list:
    found = []
    for folder in APP_FOLDERS:
        try:
            found += [i[:-4] for i in os.listdir(folder) if i.endswith(".app")]
        except OSError:
            continue
    return found


def resolve_app(name: str) -> str:
    name = (name or "").strip()
    low = name.lower()
    if low in APP_ALIASES:
        return APP_ALIASES[low]
    apps = _installed_apps()
    for app in apps:                      # exact, case-insensitive
        if app.lower() == low:
            return app
    for app in apps:                      # partial match
        if low and low in app.lower():
            return app
    return name
