import io
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from efcheck.commands import capture_session


class CaptureSessionTests(unittest.TestCase):
    def test_main_reports_missing_config_file_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "missing-settings.json"
            stderr = io.StringIO()
            with patch.object(
                capture_session,
                "parse_args",
                return_value=Namespace(config=str(config_path), site="endfield"),
            ), redirect_stderr(stderr):
                exit_code = capture_session.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("Missing file", stderr.getvalue())

    def test_main_reports_invalid_json_as_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text("{not-json}", encoding="utf-8")
            stderr = io.StringIO()
            with patch.object(
                capture_session,
                "parse_args",
                return_value=Namespace(config=str(config_path), site="endfield"),
            ), redirect_stderr(stderr):
                exit_code = capture_session.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("Configuration error", stderr.getvalue())

    def test_main_reports_invalid_config_value_types_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text(
                json.dumps({"browser_profile_dir": 123}),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with patch.object(
                capture_session,
                "parse_args",
                return_value=Namespace(config=str(config_path), site="endfield"),
            ), redirect_stderr(stderr):
                exit_code = capture_session.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("Configuration error", stderr.getvalue())

    def test_main_reports_missing_playwright_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "browser_profile_dir": "../state/browser-profile",
                        "signin_url": "https://game.skport.com/endfield/sign-in",
                    }
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            stdout = io.StringIO()
            import_exc = ImportError("playwright missing")
            real_import = __import__

            def fake_import(name, *args, **kwargs):
                if name == "playwright.sync_api":
                    raise import_exc
                return real_import(name, *args, **kwargs)

            with patch.object(
                capture_session,
                "parse_args",
                return_value=Namespace(config=str(config_path), site="endfield"),
            ), patch("builtins.__import__", side_effect=fake_import), redirect_stderr(
                stderr
            ), redirect_stdout(stdout):
                exit_code = capture_session.main()

        self.assertEqual(exit_code, 20)
        self.assertIn("Missing dependency", stderr.getvalue())

    def test_main_reports_unknown_site_as_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "sites": [
                            {
                                "key": "endfield",
                                "signin_url": "https://game.skport.com/endfield/sign-in",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with patch.object(
                capture_session,
                "parse_args",
                return_value=Namespace(config=str(config_path), site="arknights"),
            ), redirect_stderr(stderr):
                exit_code = capture_session.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("Unknown site", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
