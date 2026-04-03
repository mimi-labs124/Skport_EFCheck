import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skport_signin import cli
from skport_signin.app_paths import build_app_paths
from skport_signin.default_settings import write_default_settings


class DoctorTests(unittest.TestCase):
    def test_init_creates_default_config_in_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            stdout = io.StringIO()

            exit_code = cli.main(
                [
                    "--base-dir",
                    str(base_dir),
                    "init",
                ],
                stdout=stdout,
            )

            config_path = base_dir / "config" / "settings.json"
            self.assertTrue(config_path.exists())
            data = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(data["sites"][0]["key"], "endfield")

    def test_doctor_json_reports_missing_config_and_runtime_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            stdout = io.StringIO()

            exit_code = cli.main(
                [
                    "--base-dir",
                    str(base_dir),
                    "doctor",
                    "--json",
                ],
                stdout=stdout,
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["config_exists"])
        self.assertFalse(payload["config_valid"])
        self.assertEqual(payload["enabled_sites"], [])
        self.assertIn("config_dir", payload["path_checks"])
        self.assertIn("playwright_browsers_dir", payload["paths"])

    def test_doctor_json_reports_config_health_and_site_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            cli.main(["--base-dir", str(base_dir), "init"])
            stdout = io.StringIO()

            exit_code = cli.main(
                [
                    "--base-dir",
                    str(base_dir),
                    "doctor",
                    "--json",
                ],
                stdout=stdout,
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["config_exists"])
        self.assertTrue(payload["config_valid"])
        self.assertEqual(payload["enabled_sites"], ["endfield"])
        self.assertIn("sites", payload)
        self.assertEqual(payload["sites"][0]["key"], "endfield")
        self.assertIn("profile_dir_exists", payload["sites"][0])
        self.assertTrue(payload["path_checks"]["config_dir"]["writable"])

    def test_doctor_json_reports_invalid_config_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            config_path = base_dir / "config" / "settings.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("{not-json}", encoding="utf-8")
            stdout = io.StringIO()

            exit_code = cli.main(
                [
                    "--base-dir",
                    str(base_dir),
                    "doctor",
                    "--json",
                ],
                stdout=stdout,
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["config_exists"])
        self.assertFalse(payload["config_valid"])
        self.assertIn("Could not parse config file", payload["config_error"])

    def test_write_default_settings_uses_atomic_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            paths = build_app_paths(base_dir_override=str(base_dir))

            with patch("skport_signin.default_settings.write_text_atomic") as write_atomic:
                config_path = write_default_settings(paths, force=True)

        write_atomic.assert_called_once()
        self.assertEqual(write_atomic.call_args.args[0], config_path)
