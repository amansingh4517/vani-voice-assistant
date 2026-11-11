"""Finding files and opening them."""

import os

from vani.tools.core import error, resolve_app, resolve_path, run, tool


def _format_hits(output: str, nothing: str, limit: int) -> str:
    lines = [line for line in output.splitlines() if line]
    if not lines:
        return nothing
    shown = lines[:int(limit)]
    more = f" (and {len(lines) - len(shown)} more)" if len(lines) > len(shown) else ""
    return f"Found {len(lines)}: " + "; ".join(shown) + more


@tool
def find_files(name: str, folder: str = "home", limit: int = 15) -> str:
    """Find files or folders by name using Spotlight. folder limits where to look."""
    res = run(["mdfind", "-onlyin", resolve_path(folder), "-name", name], timeout=30)
    if not res.ok:
        return res.message()
    return _format_hits(res.output, f"Nothing found matching '{name}'.", limit)


@tool
def search_in_files(text: str, folder: str = "home", limit: int = 15) -> str:
    """Search inside file contents (and names) for some text using Spotlight."""
    res = run(["mdfind", "-onlyin", resolve_path(folder), text], timeout=30)
    if not res.ok:
        return res.message()
    return _format_hits(res.output, f"No files mention '{text}'.", limit)


@tool
def open_path(path: str) -> str:
    """Open a file or folder with its default app (folders open in Finder)."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    return run(["open", p]).message(f"Opened {os.path.basename(p) or p}.")


@tool
def open_file_with_app(path: str, app_name: str) -> str:
    """Open a file with a specific app, e.g. open a .py file with 'Visual Studio Code'."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    app = resolve_app(app_name)
    return run(["open", "-a", app, p]).message(f"Opened {os.path.basename(p)} in {app}.")


@tool
def reveal_in_finder(path: str) -> str:
    """Show a file or folder highlighted in Finder."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    return run(["open", "-R", p]).message("Shown in Finder.")
