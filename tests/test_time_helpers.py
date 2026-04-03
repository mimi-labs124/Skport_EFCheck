import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfoNotFoundError

from skport_signin.time_helpers import load_timezone


class TimeHelperTests(unittest.TestCase):
    def test_load_timezone_returns_zoneinfo_for_valid_key(self) -> None:
        timezone = load_timezone("Asia/Taipei")

        self.assertEqual(str(timezone), "Asia/Taipei")

    def test_load_timezone_raises_helpful_error_when_tzdata_is_missing(self) -> None:
        with patch(
            "skport_signin.time_helpers.ZoneInfo",
            side_effect=ZoneInfoNotFoundError("Asia/Taipei"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Install the `tzdata` package",
            ):
                load_timezone("Asia/Taipei")


if __name__ == "__main__":
    unittest.main()


