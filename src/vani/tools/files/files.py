"""Everyday file and folder operations: list, read, write, move, copy, rename, delete.

Paths can be absolute, start with ~, or start with a folder word such as
'desktop/notes.txt' or 'downloads'.
"""

import datetime
import os
import shutil

from vani.tools.core import error, human_size, is_protected, quote, resolve_path, run, run_script, tool


@tool
def list_directory(path: str = "home", show_hidden: bool = False) -> str:
    """List the files and folders inside a folder. Folders end with '/'."""
    p = resolve_path(path)
    if not os.path.isdir(p):
        return error(f"'{path}' is not a folder.")
    try:
        names = sorted(os.listdir(p), key=str.lower)
    except PermissionError:
        return error("permission denied for that folder.")
    if not show_hidden:
        names = [n for n in names if not n.startswith(".")]
    if not names:
        return "The folder is empty."
    shown = [n + "/" if os.path.isdir(os.path.join(p, n)) else n for n in names[:100]]
    extra = f" ...and {len(names) - 100} more." if len(names) > 100 else ""
    return f"{len(names)} items in {p}: " + ", ".join(shown) + extra


@tool
def get_file_info(path: str) -> str:
    """Get size, type and last modified date of a file or folder."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    st = os.stat(p)
    modified = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%d %b %Y, %I:%M %p")
    if os.path.isdir(p):
        res = run(["du", "-sh", p], timeout=60)
        size = res.output.split()[0] if res.ok and res.output else "unknown size"
        return f"Folder {p}: {size}, {len(os.listdir(p))} items, modified {modified}."
    return f"File {p}: {human_size(st.st_size)}, modified {modified}."


@tool
def read_text_file(path: str, max_chars: int = 4000) -> str:
    """Read the text content of a file (txt, md, py, csv, json, etc.)."""
    p = resolve_path(path)
    if not os.path.isfile(p):
        return error(f"'{path}' is not a file.")
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            data = f.read(int(max_chars) + 1)
    except PermissionError:
        return error("permission denied.")
    if len(data) > max_chars:
        return data[:max_chars] + "\n[...truncated]"
    return data or "The file is empty."


@tool
def write_text_file(path: str, content: str, overwrite: bool = False) -> str:
    """Create a text file with the given content. Fails if the file exists unless overwrite=true."""
    p = resolve_path(path)
    if os.path.exists(p) and not overwrite:
        return error(f"'{os.path.basename(p)}' already exists. Ask the user before overwriting.")
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        return error(str(e))
    return f"Saved {os.path.basename(p)}."


@tool
def append_text_file(path: str, content: str) -> str:
    """Add text to the end of a file. Creates the file if it does not exist."""
    p = resolve_path(path)
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(content + "\n")
    except OSError as e:
        return error(str(e))
    return f"Added to {os.path.basename(p)}."


@tool
def create_folder(path: str) -> str:
    """Create a new folder (and any missing parent folders)."""
    p = resolve_path(path)
    try:
        os.makedirs(p, exist_ok=True)
    except OSError as e:
        return error(str(e))
    return f"Folder ready: {p}"


@tool
def move_path(source: str, destination: str) -> str:
    """Move a file or folder. If destination is an existing folder, the item goes inside it."""
    src, dst = resolve_path(source), resolve_path(destination)
    if not os.path.exists(src):
        return error(f"'{source}' does not exist.")
    if is_protected(src):
        return error("that location is protected.")
    final = os.path.join(dst, os.path.basename(src)) if os.path.isdir(dst) else dst
    if os.path.exists(final):
        return error(f"'{os.path.basename(final)}' already exists at the destination.")
    try:
        shutil.move(src, final)
    except OSError as e:
        return error(str(e))
    return f"Moved to {final}."


@tool
def copy_path(source: str, destination: str) -> str:
    """Copy a file or folder. If destination is an existing folder, the copy goes inside it."""
    src, dst = resolve_path(source), resolve_path(destination)
    if not os.path.exists(src):
        return error(f"'{source}' does not exist.")
    final = os.path.join(dst, os.path.basename(src)) if os.path.isdir(dst) else dst
    if os.path.exists(final):
        return error(f"'{os.path.basename(final)}' already exists at the destination.")
    try:
        if os.path.isdir(src):
            shutil.copytree(src, final)
        else:
            shutil.copy2(src, final)
    except OSError as e:
        return error(str(e))
    return f"Copied to {final}."


@tool
def rename_path(path: str, new_name: str) -> str:
    """Rename a file or folder. new_name is just the new name, not a full path."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    if is_protected(p):
        return error("that location is protected.")
    if "/" in new_name:
        return error("new_name must be a name only, without slashes.")
    target = os.path.join(os.path.dirname(p), new_name)
    if os.path.exists(target):
        return error(f"'{new_name}' already exists.")
    os.rename(p, target)
    return f"Renamed to {new_name}."


@tool
def delete_path(path: str) -> str:
    """Move a file or folder to the Trash (recoverable). Ask the user to confirm first."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    if is_protected(p):
        return error("that location is protected and cannot be deleted.")
    res = run_script(f'tell application "Finder" to delete POSIX file "{quote(p)}"')
    return res.message(f"Moved {os.path.basename(p)} to the Trash.")


@tool
def empty_trash(confirmed: bool = False) -> str:
    """Permanently empty the Trash. Only call with confirmed=true AFTER the user clearly said yes."""
    if not confirmed:
        return error("not confirmed. Ask the user to confirm first.")
    return run_script('tell application "Finder" to empty trash', timeout=120).message("Trash emptied.")
