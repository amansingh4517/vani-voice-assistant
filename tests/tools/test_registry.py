"""Tests for tool registration, metadata, and category discovery."""

import pytest

from vani.tools import TOOL_MAP, get_tools, registry


def test_every_tool_has_docstring_and_category():
    assert len(TOOL_MAP) > 60
    for fn in TOOL_MAP.values():
        assert fn.__doc__, fn.__name__
        assert fn.__tool_category__


def test_category_filter():
    names = {f.__name__ for f in get_tools("power")}
    assert names == {
        "lock_screen",
        "sleep_display",
        "sleep_mac",
        "restart_mac",
        "shut_down_mac",
    }


def test_duplicate_tool_name_rejected():
    with pytest.raises(ValueError):
        registry.register(TOOL_MAP["open_app"])
