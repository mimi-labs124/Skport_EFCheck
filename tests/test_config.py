import json
import tempfile
import unittest
from pathlib import Path

from efcheck.config import load_runtime_settings
from efcheck.errors import ConfigError


class ConfigTests(unittest.TestCase):
    def test_load_runtime_settings_requires_real_json_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text(
                json.dumps({"headless": "false"}),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_runtime_settings(config_path, "https://example.com")

    def test_load_runtime_settings_rejects_non_string_signin_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            config_path.write_text(
                json.dumps({"signin_url": 123}),
                encoding="utf-8",
            )

            with self.assertRaises(ConfigError):
                load_runtime_settings(config_path, "https://example.com")


if __name__ == "__main__":
    unittest.main()
