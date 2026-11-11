# Adding a New Tool

Tools live under `src/vani/tools/` and are auto-discovered at import time using `pkgutil.walk_packages`.

## Conventions

1. **Use the plain `@tool` decorator** (no arguments):
   ```python
   from vani.tools.core import error, run, tool


   @tool
   def my_new_tool(name: str, count: int = 5) -> str:
       """Short one-line description used by the LLM to understand this tool."""
       if count < 1:
           return error("count must be at least 1.")
       return run(["echo", name]).message(f"Ran for {name}.")
   ```
2. **Import core helpers from `vani.tools.core`** (never use relative `.core` imports).
3. **Never call `subprocess` directly** inside a tool module. Always use `run(...)`, `run_script(...)`, or `get_runner()` from `vani.tools.core` so unit tests can swap in `FakeRunner`.
4. **Provide clear type hints and a docstring** — Ollama generates the JSON tool schema directly from the function signature and docstring.
5. **Do not rename existing tool functions** if the prompt or tests reference them.

## Categories

`ToolRegistry.register` sets `__tool_category__` from the **last segment** of the module's dotted path. For example:

- `vani.tools.system.power` → category `"power"`
- `vani.tools.files.files` → category `"files"`

Adding a new `.py` file under any `src/vani/tools/` subpackage (excluding `core/` and `tests/`) automatically registers its `@tool` functions into `ALL_TOOLS` and `TOOL_MAP`.

## Destructive Actions

For irreversible actions, require an explicit `confirmed: bool = False` parameter:

```python
@tool
def wipe_cache(confirmed: bool = False) -> str:
    """Clear the app cache. Ask the user to confirm before passing confirmed=True."""
    if not confirmed:
        return error("Ask the user to confirm before clearing the cache, then call again with confirmed=True.")
    ...
```
