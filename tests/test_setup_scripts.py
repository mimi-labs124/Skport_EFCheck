from pathlib import Path
import unittest


class SetupScriptTests(unittest.TestCase):
    def test_setup_windows_has_fail_fast_guards_for_dependency_steps(self) -> None:
        script = Path("setup_windows.bat").read_text(encoding="utf-8")

        self.assertIn("python -m pip install -r requirements.txt", script)
        self.assertIn("playwright install chromium", script)
        self.assertGreaterEqual(script.count("if errorlevel 1 exit /b 1"), 3)


if __name__ == "__main__":
    unittest.main()
