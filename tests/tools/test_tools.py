"""Tests run on any OS: a FakeRunner replaces the real command runner."""

import os
import tempfile
import unittest

from vani.tools import TOOL_MAP, get_tools, registry, set_runner
from vani.tools.core.runner import CommandResult, SubprocessRunner


class FakeRunner:
    def __init__(self, ok=True, output=""):
        self.ok, self.output, self.calls, self.detached = ok, output, [], []

    def run(self, args, timeout=30, input_text=None):
        self.calls.append(list(args))
        return CommandResult(self.ok, self.output)

    def spawn_detached(self, args):
        self.detached.append(list(args))


class ToolTests(unittest.TestCase):
    def tearDown(self):
        set_runner(SubprocessRunner())

    def test_every_tool_has_docstring_and_category(self):
        self.assertGreater(len(TOOL_MAP), 60)
        for fn in TOOL_MAP.values():
            self.assertTrue(fn.__doc__, fn.__name__)
            self.assertTrue(fn.__tool_category__)

    def test_category_filter(self):
        names = {f.__name__ for f in get_tools("power")}
        self.assertEqual(names, {"lock_screen", "sleep_display", "sleep_mac",
                                 "restart_mac", "shut_down_mac"})

    def test_open_app_uses_runner(self):
        fake = FakeRunner()
        set_runner(fake)
        self.assertEqual(TOOL_MAP["open_app"]("chrome"), "Opened Google Chrome.")
        self.assertEqual(fake.calls[0], ["open", "-a", "Google Chrome"])

    def test_failure_becomes_error_string(self):
        set_runner(FakeRunner(ok=False, output="boom"))
        self.assertEqual(TOOL_MAP["set_volume"](30), "Error: boom")

    def test_confirmation_required(self):
        fake = FakeRunner()
        set_runner(fake)
        self.assertTrue(TOOL_MAP["shut_down_mac"]().startswith("Error:"))
        self.assertTrue(TOOL_MAP["empty_trash"]().startswith("Error:"))
        self.assertEqual(fake.calls, [])

    def test_shell_blocklist(self):
        fake = FakeRunner()
        set_runner(fake)
        self.assertTrue(TOOL_MAP["run_shell_command"]("sudo ls").startswith("Error:"))
        self.assertEqual(fake.calls, [])

    def test_timer_spawns_detached(self):
        fake = FakeRunner()
        set_runner(fake)
        self.assertEqual(TOOL_MAP["set_timer"](90, "Tea"), "Timer set for 1 minute and 30 seconds.")
        self.assertEqual(len(fake.detached), 1)

    def test_calculate(self):
        self.assertEqual(TOOL_MAP["calculate"]("(12+8)*3/4"), "(12+8)*3/4 = 15")
        self.assertEqual(TOOL_MAP["calculate"]("2^10"), "2^10 = 1024")
        self.assertTrue(TOOL_MAP["calculate"]("__import__('os')").startswith("Error:"))

    def test_file_tools_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "a.txt")
            self.assertEqual(TOOL_MAP["write_text_file"](f, "hi"), "Saved a.txt.")
            self.assertTrue(TOOL_MAP["write_text_file"](f, "x").startswith("Error:"))
            self.assertEqual(TOOL_MAP["read_text_file"](f), "hi")
            self.assertEqual(TOOL_MAP["rename_path"](f, "b.txt"), "Renamed to b.txt.")
            self.assertIn("b.txt", TOOL_MAP["list_directory"](d))

    def test_organizer_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            for n in ("p.png", "r.pdf", "z.xyz"):
                open(os.path.join(d, n), "w").close()
            msg = TOOL_MAP["organize_folder"](d, dry_run=True)
            self.assertIn("1 to Images", msg)
            self.assertIn("1 to Other", msg)

    def test_play_song_uses_runner(self):
        fake = FakeRunner()
        set_runner(fake)
        msg = TOOL_MAP["play_song"]("Shape of You")
        self.assertTrue("YouTube Music" in msg)
        self.assertTrue(len(fake.calls) > 0)
        self.assertEqual(fake.calls[0][0], "open")

    def test_duplicate_tool_name_rejected(self):
        with self.assertRaises(ValueError):
            registry.register(TOOL_MAP["open_app"])


if __name__ == "__main__":
    unittest.main()
