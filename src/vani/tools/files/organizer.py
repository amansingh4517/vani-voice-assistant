"""Sorting a messy folder into sub-folders by file type.

To support a new kind of file, add a line to FILE_CATEGORIES. Nothing else changes.
"""

import os
import shutil

from .core import error, is_protected, resolve_path, tool

FILE_CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".svg", ".bmp", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".pages", ".ppt", ".pptx",
                  ".xls", ".xlsx", ".csv", ".key", ".numbers", ".rtf"},
    "Videos": {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".dmg", ".pkg"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".html", ".css",
             ".json", ".sh", ".go", ".rs", ".ipynb"},
}
_ALLOWED_PROTECTED = ("Downloads", "Desktop", "Documents")


def _category_for(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return next((c for c, exts in FILE_CATEGORIES.items() if ext in exts), "Other")


@tool
def organize_folder(path: str = "downloads", dry_run: bool = False) -> str:
    """Sort loose files in a folder into subfolders by type (Images, Documents, Videos, Audio, Archives, Code, Other). Ask the user first. dry_run=true only previews."""
    p = resolve_path(path)
    if not os.path.isdir(p):
        return error(f"'{path}' is not a folder.")
    if is_protected(p) and os.path.basename(p) not in _ALLOWED_PROTECTED:
        return error("that folder is protected.")
    plan = {}
    for name in os.listdir(p):
        if name.startswith(".") or not os.path.isfile(os.path.join(p, name)):
            continue
        plan.setdefault(_category_for(name), []).append(name)
    if not plan:
        return "No loose files to organize."
    summary = ", ".join(f"{len(v)} to {k}" for k, v in plan.items())
    if dry_run:
        return f"Would move: {summary}."
    for category, files in plan.items():
        os.makedirs(os.path.join(p, category), exist_ok=True)
        for name in files:
            target = os.path.join(p, category, name)
            if not os.path.exists(target):
                shutil.move(os.path.join(p, name), target)
    return f"Organized: {summary}."
