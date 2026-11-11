"""Tool registry (Open/Closed principle).

New tools are added by decorating a function with @tool. Nothing in this file,
or in any existing tool module, has to change.

The category of a tool is the name of the module it lives in, so
vani/tools/files/files.py -> category "files".
"""

from typing import Callable, Dict, List


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        name = func.__name__
        if name in self._tools:
            raise ValueError(f"Duplicate tool name: {name}")
        func.__tool_category__ = func.__module__.rsplit(".", 1)[-1]
        self._tools[name] = func
        return func

    def all(self) -> List[Callable]:
        return list(self._tools.values())

    def get(self, name: str) -> Callable:
        return self._tools[name]

    def categories(self) -> List[str]:
        return sorted({f.__tool_category__ for f in self._tools.values()})

    def by_category(self, *categories: str) -> List[Callable]:
        wanted = set(categories)
        return [f for f in self._tools.values() if f.__tool_category__ in wanted]


registry = ToolRegistry()


def tool(func: Callable) -> Callable:
    """Decorator: register `func` as an assistant tool. Returns it unchanged,
    so its name, type hints and docstring still reach your LLM framework."""
    return registry.register(func)
