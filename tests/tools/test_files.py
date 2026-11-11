"""Tests for file and organizer tools."""

import os
import tempfile

from vani.tools import TOOL_MAP


def test_confirmation_required_for_empty_trash(fake_runner):
    assert TOOL_MAP["empty_trash"]().startswith("Error:")
    assert fake_runner.calls == []


def test_file_tools_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "a.txt")
        assert TOOL_MAP["write_text_file"](f, "hi") == "Saved a.txt."
        assert TOOL_MAP["write_text_file"](f, "x").startswith("Error:")
        assert TOOL_MAP["read_text_file"](f) == "hi"
        assert TOOL_MAP["rename_path"](f, "b.txt") == "Renamed to b.txt."
        assert "b.txt" in TOOL_MAP["list_directory"](d)


def test_organizer_dry_run():
    with tempfile.TemporaryDirectory() as d:
        for n in ("p.png", "r.pdf", "z.xyz"):
            open(os.path.join(d, n), "w").close()
        msg = TOOL_MAP["organize_folder"](d, dry_run=True)
        assert "1 to Images" in msg
        assert "1 to Other" in msg
