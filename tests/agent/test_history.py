"""Tests for conversation history trimming."""

from types import SimpleNamespace

from vani.agent.history import trim_history


def test_keeps_all_when_within_limit():
    msgs = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "u1"},
        {"role": "assistant", "content": "a1"},
        {"role": "user", "content": "u2"},
        {"role": "assistant", "content": "a2"},
    ]
    assert trim_history(msgs, keep_turns=2) == msgs


def test_keeps_system_and_last_n_user_turns_without_splitting_tool_calls():
    msgs = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "u1"},
        SimpleNamespace(role="assistant", tool_calls=[{"name": "t1"}]),
        {"role": "tool", "tool_name": "t1", "content": "res1"},
        SimpleNamespace(role="assistant", content="a1"),
        {"role": "user", "content": "u2"},
        SimpleNamespace(role="assistant", tool_calls=[{"name": "t2"}]),
        {"role": "tool", "tool_name": "t2", "content": "res2"},
        SimpleNamespace(role="assistant", content="a2"),
        {"role": "user", "content": "u3"},
        {"role": "assistant", "content": "a3"},
    ]

    trimmed = trim_history(msgs, keep_turns=2)

    assert trimmed[0] == {"role": "system", "content": "sys"}
    assert trimmed[1] == {"role": "user", "content": "u2"}
    assert len(trimmed) == 7
    # Tool call and its tool result from turn 2 remain intact together
    assert trimmed[2].role == "assistant"
    assert trimmed[3]["role"] == "tool"
    assert trimmed[-1] == {"role": "assistant", "content": "a3"}


def test_supports_object_messages_throughout():
    msgs = [
        SimpleNamespace(role="system", content="sys"),
        SimpleNamespace(role="user", content="u1"),
        SimpleNamespace(role="assistant", content="a1"),
        SimpleNamespace(role="user", content="u2"),
        SimpleNamespace(role="assistant", content="a2"),
    ]
    trimmed = trim_history(msgs, keep_turns=1)
    assert [m.content for m in trimmed] == ["sys", "u2", "a2"]
