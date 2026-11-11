"""Zip and unzip."""

import os

from vani.tools.core import error, resolve_path, run, tool


@tool
def zip_path(path: str) -> str:
    """Compress a file or folder into a .zip file next to it."""
    p = resolve_path(path)
    if not os.path.exists(p):
        return error(f"'{path}' does not exist.")
    dest = p.rstrip("/") + ".zip"
    res = run(["ditto", "-c", "-k", "--keepParent", p, dest], timeout=300)
    return res.message(f"Created {os.path.basename(dest)}.")


@tool
def unzip_file(path: str, destination: str = "") -> str:
    """Extract a .zip file. By default extracts next to the zip into a folder of the same name."""
    p = resolve_path(path)
    if not os.path.isfile(p):
        return error(f"'{path}' is not a file.")
    if destination:
        dest = resolve_path(destination)
    else:
        dest = p[:-4] if p.lower().endswith(".zip") else p + "_unzipped"
    os.makedirs(dest, exist_ok=True)
    return run(["ditto", "-x", "-k", p, dest], timeout=300).message(f"Extracted to {dest}.")
