import io
import json
import tempfile
import unittest
from pathlib import Path

from skport_signin import cli


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
        self.assertIn("playwright_browsers_dir", payload["paths"])


