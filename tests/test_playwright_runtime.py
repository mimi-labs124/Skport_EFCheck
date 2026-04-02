import tempfile
import unittest
from pathlib import Path

from efcheck.playwright_runtime import ensure_browser_runtime_available


class _FakeChromium:
    def __init__(self, executable_path: str) -> None:
        self.executable_path = executable_path


class _FakePlaywright:
    def __init__(self, executable_path: str) -> None:
        self.chromium = _FakeChromium(executable_path)


class PlaywrightRuntimeTests(unittest.TestCase):
    def test_packaged_mode_missing_browser_runtime_has_packaged_hint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_path = str(Path(temp_dir) / "missing-browser.exe")
            playwright = _FakePlaywright(executable_path)
            paths = type("Paths", (), {"mode": "packaged"})()

            with self.assertRaises(FileNotFoundError) as cm:
                ensure_browser_runtime_available(playwright, paths)

        self.assertIn("doctor --install-browser", str(cm.exception))

    def test_source_mode_missing_browser_runtime_has_source_hint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable_path = str(Path(temp_dir) / "missing-browser.exe")
            playwright = _FakePlaywright(executable_path)
            paths = type("Paths", (), {"mode": "source"})()

            with self.assertRaises(FileNotFoundError) as cm:
                ensure_browser_runtime_available(playwright, paths)

        self.assertIn("playwright install chromium", str(cm.exception))
