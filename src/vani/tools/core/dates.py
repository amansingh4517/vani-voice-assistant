"""Date parsing and AppleScript date building."""

import datetime


def parse_datetime(text: str) -> datetime.datetime:
    """Parse 'YYYY-MM-DD HH:MM' (also with a T, with seconds, or date only)."""
    text = text.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError("Use the format YYYY-MM-DD HH:MM, for example 2026-11-08 17:30.")


def applescript_date_lines(var: str, dt: datetime.datetime) -> str:
    """AppleScript lines that build a locale-independent date in variable `var`."""
    return (
        f"set {var} to current date\n"
        f"set day of {var} to 1\n"
        f"set year of {var} to {dt.year}\n"
        f"set month of {var} to {dt.month}\n"
        f"set day of {var} to {dt.day}\n"
        f"set hours of {var} to {dt.hour}\n"
        f"set minutes of {var} to {dt.minute}\n"
        f"set seconds of {var} to 0\n"
    )
