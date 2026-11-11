"""Single place that defines what a tool result looks like.

Every tool returns a short string. Failures start with "Error: " so both the
LLM and your own code can recognise them.
"""

ERROR_PREFIX = "Error: "


def error(message: str) -> str:
    return f"{ERROR_PREFIX}{message}"


def is_error(text: str) -> bool:
    return text.startswith(ERROR_PREFIX)
