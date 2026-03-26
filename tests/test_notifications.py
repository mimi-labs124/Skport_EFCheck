import unittest
from unittest.mock import patch

from efcheck.notifications import notify_status, should_notify_status


class NotificationTests(unittest.TestCase):
    def test_session_expired_requires_notification(self) -> None:
        self.assertTrue(should_notify_status("SESSION_EXPIRED"))

    def test_success_does_not_require_notification(self) -> None:
        self.assertFalse(should_notify_status("SUCCESS"))

    def test_notification_ignores_missing_powershell_executable(self) -> None:
        with patch(
            "efcheck.notifications.subprocess.run",
            side_effect=FileNotFoundError("powershell"),
        ):
            notify_status("SESSION_EXPIRED", "title", "message")


if __name__ == "__main__":
    unittest.main()
