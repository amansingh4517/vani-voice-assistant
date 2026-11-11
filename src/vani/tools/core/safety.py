"""Safety policy for the shell tool, kept apart from the tool itself so the
rules can change without touching it."""

import re

_BLOCKED = re.compile(
    r"(\bsudo\b|\brm\s+-[a-z]*r|\bmkfs\b|\bdiskutil\s+(erase|partition|apfs\s+delete)|"
    r"\bdd\s+if=|:\(\)\s*\{|>\s*/dev/|\bchmod\s+-R\s+777\s+/|\bshutdown\b|\breboot\b|"
    r"\bcurl\b.*\|\s*(ba)?sh|\bwget\b.*\|\s*(ba)?sh)", re.IGNORECASE)


def is_dangerous_shell(command: str) -> bool:
    return bool(_BLOCKED.search(command))
