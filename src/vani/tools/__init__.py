"""vani.tools - tools for a Mac voice assistant, one module per kind of tool.

Usage:
    from vani.tools import ALL_TOOLS, get_tools, open_app

    get_tools("files", "file_search")      # only some categories
    registry.categories()                  # see what exists

Adding a tool: write a function with type hints and a docstring in any module
inside this folder and put @tool above it. Adding a new module? Just drop the
file in - it is discovered automatically. No existing file needs editing.
"""

import importlib
import pkgutil

from vani.tools.core import registry, set_runner

for _importer, _mod_name, _is_pkg in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
    if not _is_pkg and "core" not in _mod_name.split(".") and "tests" not in _mod_name.split("."):
        importlib.import_module(_mod_name)

ALL_TOOLS = registry.all()
TOOL_MAP = {fn.__name__: fn for fn in ALL_TOOLS}


def get_tools(*categories: str) -> list:
    """Return the tools in the given categories (module names). No arguments = all tools."""
    return registry.by_category(*categories) if categories else registry.all()


globals().update(TOOL_MAP)
__all__ = ["ALL_TOOLS", "TOOL_MAP", "get_tools", "registry", "set_runner", *TOOL_MAP]
