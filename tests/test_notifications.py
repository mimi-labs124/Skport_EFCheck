import unittest
from unittest.mock import patch

from skport_signin.notifications import notify_status, should_notify_status


class NotificationTests(unittest.TestCase):
    def test_session_expired_requires_notification(self) -> None:
        self.assertTrue(should_notify_status("SESSION_EXPIRED"))

    def test_error_requires_notification(self) -> None:
        self.assertTrue(should_notify_status("ERROR"))

    def test_success_does_not_require_notification(self) -> None:
        self.assertFalse(should_notify_status("SUCCESS"))

    def test_notification_reports_missing_powershell_executable(self) -> None:
        with patch("skport_signin.notifications.shutil.which", return_value=None):
            message = notify_status("SESSION_EXPIRED", "title", "message")

        self.assertIn("no PowerShell executable", message)

    def test_notification_reports_subprocess_failures(self) -> None:
        with patch("skport_signin.notifications.shutil.which", return_value="powershell"), patch(
            "skport_signin.notifications.subprocess.run",
            side_effect=FileNotFoundError("powershell"),
        ):
            message = notify_status("SESSION_EXPIRED", "title", "message")

        self.assertIn("Notification failed", message)

    def test_notification_reports_nonzero_return_code(self) -> None:
        class Completed:
            returncode = 1
            stderr = "toast failed"

        with patch("skport_signin.notifications.shutil.which", return_value="powershell"), patch(
            "skport_signin.notifications.subprocess.run",
            return_value=Completed(),
        ):
            message = notify_status("SESSION_EXPIRED", "title", "message")

        self.assertIn("exited with code 1", message)
        self.assertIn("toast failed", message)


if __name__ == "__main__":
    unittest.main()

