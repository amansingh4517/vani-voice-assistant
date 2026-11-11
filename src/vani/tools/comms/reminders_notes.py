"""Reminders and Notes apps."""

from vani.tools.core import (applescript_date_lines, error, parse_datetime, quote,
                   run_script, tool)


@tool
def create_reminder(title: str, due: str = "") -> str:
    """Add a reminder in the Reminders app. due is optional, format 'YYYY-MM-DD HH:MM' (24-hour)."""
    if due:
        try:
            when = parse_datetime(due)
        except ValueError as e:
            return error(str(e))
        script = ('tell application "Reminders"\n' + applescript_date_lines("d", when) +
                  f'make new reminder with properties {{name:"{quote(title)}", due date:d}}\n'
                  'end tell')
    else:
        script = ('tell application "Reminders" to make new reminder '
                  f'with properties {{name:"{quote(title)}"}}')
    return run_script(script).message(f"Reminder added: {title}.")


@tool
def list_reminders() -> str:
    """List the reminders that are not completed yet."""
    res = run_script('tell application "Reminders" to get name of '
                     '(reminders whose completed is false)', timeout=60)
    if not res.ok:
        return res.message()
    return f"Open reminders: {res.output}" if res.output else "You have no open reminders."


@tool
def create_note(title: str, body: str = "") -> str:
    """Create a new note in the Notes app."""
    html = quote(f"<h1>{title}</h1>" + body.replace("\n", "<br>"))
    script = f'tell application "Notes" to make new note with properties {{body:"{html}"}}'
    return run_script(script).message(f"Note created: {title}.")
