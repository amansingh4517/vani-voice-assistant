"""Calendar app. Dates use 'YYYY-MM-DD HH:MM' (24-hour)."""

import datetime

from .core import (applescript_date_lines, error, parse_datetime, quote,
                   run_script, tool)


@tool
def create_calendar_event(title: str, start: str, end: str = "", location: str = "") -> str:
    """Add an event to Calendar. start and end use 'YYYY-MM-DD HH:MM' (24-hour). If end is empty the event lasts one hour."""
    try:
        s = parse_datetime(start)
        e = parse_datetime(end) if end else s + datetime.timedelta(hours=1)
    except ValueError as err:
        return error(str(err))
    props = f'summary:"{quote(title)}", start date:s, end date:e'
    if location:
        props += f', location:"{quote(location)}"'
    script = ('tell application "Calendar"\n' + applescript_date_lines("s", s) +
              applescript_date_lines("e", e) +
              'tell (first calendar whose writable is true)\n'
              f'make new event with properties {{{props}}}\n'
              'end tell\nend tell')
    return run_script(script, timeout=60).message(
        f"Event added: {title} on {s.strftime('%A %d %B at %I:%M %p')}.")


@tool
def get_calendar_events(days: int = 1) -> str:
    """List calendar events from today for the next N days (1 = today, 7 = this week)."""
    days = max(1, min(30, int(days)))
    script = (
        'set s to current date\n'
        'set time of s to 0\n'
        f'set e to s + ({days} * days)\n'
        'set out to ""\n'
        'tell application "Calendar"\n'
        'repeat with c in calendars\n'
        'set evs to (every event of c whose start date >= s and start date < e)\n'
        'repeat with ev in evs\n'
        'set out to out & (summary of ev) & " on " & (date string of (start date of ev)) '
        '& " at " & (time string of (start date of ev)) & "; "\n'
        'end repeat\nend repeat\nend tell\nreturn out')
    res = run_script(script, timeout=90)
    if not res.ok:
        return res.message()
    return res.output or "No events in that period."
