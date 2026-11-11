"""Path handling and path safety rules."""

import os

FOLDER_ALIASES = {
    "home": "~",
    "desktop": "~/Desktop",
    "downloads": "~/Downloads",
    "documents": "~/Documents",
    "pictures": "~/Pictures",
    "photos": "~/Pictures",
    "music": "~/Music",
    "movies": "~/Movies",
    "videos": "~/Movies",
    "applications": "/Applications",
}

_SYSTEM_PATHS = {"/", "/System", "/Library", "/Applications", "/Users", "/usr",
                 "/bin", "/sbin", "/etc", "/var", "/private"}
_HOME_SUBFOLDERS = ("Desktop", "Documents", "Downloads", "Pictures", "Music",
                    "Movies", "Library")


def resolve_path(p: str) -> str:
    """Turn a spoken or typed path ('downloads/a.txt', '~/x') into an absolute path."""
    p = (p or "").strip().strip("\"'")
    if not p:
        return os.path.expanduser("~")
    head, _, rest = p.replace("\\", "/").partition("/")
    if head.lower() in FOLDER_ALIASES:
        base = os.path.expanduser(FOLDER_ALIASES[head.lower()])
        p = os.path.join(base, rest) if rest else base
    return os.path.abspath(os.path.expanduser(p))


def is_protected(path: str) -> bool:
    """True for system folders, the home folder and its main sub-folders."""
    home = os.path.expanduser("~")
    protected = set(_SYSTEM_PATHS) | {home}
    protected |= {os.path.join(home, d) for d in _HOME_SUBFOLDERS}
    return os.path.abspath(path) in protected


def human_size(n: float) -> str:
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "bytes" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} bytes"
