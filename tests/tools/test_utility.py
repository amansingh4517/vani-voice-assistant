"""Tests for utility tools."""

from vani.tools import TOOL_MAP


def test_calculate():
    assert TOOL_MAP["calculate"]("(12+8)*3/4") == "(12+8)*3/4 = 15"
    assert TOOL_MAP["calculate"]("2^10") == "2^10 = 1024"
    assert TOOL_MAP["calculate"]("__import__('os')").startswith("Error:")
