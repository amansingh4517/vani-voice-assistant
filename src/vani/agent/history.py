"""Conversation history management."""


def trim_history(messages: list, keep_turns: int = 8) -> list:
    """Keep the system prompt + last few user turns, cutting only at a user
    message so a tool call is never separated from its result."""
    role = lambda m: m["role"] if isinstance(m, dict) else m.role
    users = [i for i, m in enumerate(messages) if role(m) == "user"]
    if len(users) <= keep_turns:
        return messages
    return messages[:1] + messages[users[-keep_turns]:]
