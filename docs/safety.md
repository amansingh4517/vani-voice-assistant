# Safety & Guardrails

Vani includes multiple layers of defense against accidental or unsafe system actions:

1. **Path Protection (`vani.tools.core.paths`)**
   - `is_protected()` blocks deletion or bulk organization of system directories (`/System`, `/Library`, `/Applications`, `/usr`, `/bin`, `/sbin`, `/etc`, `/var`), the user's home directory, and top-level home subfolders (`Desktop`, `Documents`, `Downloads`, `Pictures`, `Music`, `Movies`, `Public`, `Library`).
   - Deletions move items to the macOS Trash rather than calling `rm -rf`.
2. **Shell Blocklist (`vani.tools.core.safety`)**
   - `is_dangerous_shell()` rejects shell commands matching destructive patterns (such as `sudo`, `rm -rf`, `mkfs`, `dd`, `chmod -R 777 /`, and curl/wget piped to shell) before execution.
3. **Confirmation Gates**
   - Destructive tools (`shut_down_mac`, `restart_mac`, `empty_trash`) require `confirmed=True` and return an error prompt if called without confirmation.
   - `vani.agent.prompt` instructs the LLM to ask a yes/no confirmation question before deleting/overwriting files, sending messages/emails, shutting down/restarting, or moving many files.
4. **Tool Loop Limit (`vani.agent.engine`)**
   - `MAX_STEPS = 6` bounds multi-step tool chaining per turn to prevent infinite loops.
5. **False Exit Prevention (`vani.app`)**
   - `EXIT_SIGNAL` is intercepted in `engine.py` before reaching the LLM again.
   - `app.py` verifies the user's utterance actually matches `QUIT_KEYWORDS` before shutting down, rolling back false exit turns with `del messages[checkpoint:]`.
6. **AST-Safe Math (`vani.tools.utility.calculator`)**
   - `calculate()` parses expressions with Python's `ast` module and evaluates only whitelisted operators and math functions—never calling `eval()`.
7. **Error Rollback (`vani.app`)**
   - If `process_prompt()` raises an exception, `app.py` slices `messages` back to `checkpoint` so failed turns do not corrupt conversation history.
