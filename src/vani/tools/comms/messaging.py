"""Sending messages and email."""

from vani.tools.core import quote, run_script, tool


@tool
def send_imessage(recipient: str, message: str) -> str:
    """Send an iMessage or text. recipient is a phone number or Apple ID email. Ask the user to confirm first."""
    script = ('tell application "Messages"\n'
              'set svc to 1st service whose service type = iMessage\n'
              f'set buddy1 to buddy "{quote(recipient)}" of svc\n'
              f'send "{quote(message)}" to buddy1\nend tell')
    return run_script(script, timeout=45).message(f"Message sent to {recipient}.")


@tool
def compose_email(to: str, subject: str, body: str, send_now: bool = False) -> str:
    """Create an email in Mail. By default it stays as an open draft; send_now=true sends it (confirm with the user first)."""
    script = ('tell application "Mail"\n'
              'set m to make new outgoing message with properties '
              f'{{subject:"{quote(subject)}", content:"{quote(body)}", visible:true}}\n'
              f'tell m to make new to recipient with properties {{address:"{quote(to)}"}}\n'
              + ('send m\n' if send_now else 'activate\n') + 'end tell')
    done = f"Email sent to {to}." if send_now else f"Draft email to {to} is open in Mail."
    return run_script(script, timeout=45).message(done)
