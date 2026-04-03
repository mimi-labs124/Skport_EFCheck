import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skport_signin import cli


class SetupCommandTests(unittest.TestCase):
    def test_setup_interactive_writes_config_and_shares_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            stdout = io.StringIO()

            with patch(
                "builtins.input",
                side_effect=["Y", "Y", "Y", "N", "N"],
            ), patch(
                "skport_signin.commands.setup.capture_session_command.run_capture_session"
            ) as capture_mock, patch(
                "skport_signin.commands.setup.register_task_command.handle_command"
            ) as register_mock:
                exit_code = cli.main(
                    [
                        "--base-dir",
                        str(base_dir),
                        "setup",
                        "--interactive",
                    ],
                    stdout=stdout,
                )

            config_path = base_dir / "config" / "settings.json"
            data = json.loads(config_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual([site["enabled"] for site in data["sites"]], [True, True])
        self.assertEqual(
            data["sites"][0]["browser_profile_dir"],
            data["sites"][1]["browser_profile_dir"],
        )
        capture_mock.assert_not_called()
        register_mock.assert_not_called()
        self.assertIn("Skport_Signin setup flow finished.", stdout.getvalue())

    def test_setup_interactive_runs_capture_and_register_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "portable"
            stdout = io.StringIO()

            with patch(
                "builtins.input",
                side_effect=["Y", "N", "Y", "Y"],
            ), patch(
                "skport_signin.commands.setup.capture_session_command.run_capture_session",
                return_value=0,
            ) as capture_mock, patch(
                "skport_signin.commands.setup.register_task_command.handle_command",
                return_value=0,
            ) as register_mock:
                exit_code = cli.main(
                    [
                        "--base-dir",
                        str(base_dir),
                        "setup",
                        "--interactive",
                    ],
                    stdout=stdout,
                )

        self.assertEqual(exit_code, 0)
        capture_mock.assert_called_once()
        self.assertEqual(capture_mock.call_args.kwargs["site_name"], "endfield")
        register_mock.assert_called_once()
