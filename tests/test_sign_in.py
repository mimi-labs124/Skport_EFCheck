import io
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr
from datetime import timezone
from pathlib import Path
from unittest.mock import patch

import sign_in
from efcheck.errors import InteractionError, StateFileError
from efcheck.statuses import SUCCESS


class _FakeResponse:
    def __init__(
        self,
        status: int,
        payload: dict | None = None,
        ok: bool = True,
        *,
        method: str = "GET",
        url: str = "https://zonai.skport.com/web/v1/game/endfield/attendance",
    ) -> None:
        self.status = status
        self._payload = payload or {}
        self.ok = ok
        self.url = url
        self.request = type("Request", (), {"method": method})()

    def json(self) -> dict:
        return self._payload


class _FakeExpectResponse:
    def __init__(self, response: _FakeResponse) -> None:
        self.value = response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class _BodyLocator:
    def __init__(self, text: str) -> None:
        self._text = text

    def inner_text(self, timeout: int = 2000) -> str:
        return self._text


class _CountLocator:
    def __init__(self, count: int) -> None:
        self._count = count

    def count(self) -> int:
        return self._count


class _FakePage:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)
        self.url = "https://game.skport.com/endfield/sign-in"
        self.body_text = ""
        self.login_form_count = 0

    def set_default_timeout(self, timeout_ms: int) -> None:
        return None

    def expect_response(self, predicate, timeout: int):
        for index, response in enumerate(self._responses):
            if predicate(response):
                self._responses.pop(index)
                return _FakeExpectResponse(response)
        raise AssertionError("No queued response matched the expected predicate")

    def goto(self, url: str, wait_until: str) -> None:
        return None

    def wait_for_timeout(self, timeout_ms: int) -> None:
        return None

    def reload(self, wait_until: str) -> None:
        return None

    def locator(self, selector: str):
        if selector == "body":
            return _BodyLocator(self.body_text)
        if "password" in selector:
            return _CountLocator(self.login_form_count)
        raise AssertionError("click_day_tile should be mocked in this test")

    def get_by_text(self, text: str, exact: bool = False):
        raise AssertionError("click_day_tile should be mocked in this test")


class _FakeContext:
    def __init__(self, page: _FakePage) -> None:
        self.pages = []
        self._page = page

    def new_page(self) -> _FakePage:
        return self._page

    def close(self) -> None:
        return None


class _FakeChromium:
    def __init__(self, context: _FakeContext) -> None:
        self._context = context

    def launch_persistent_context(self, *args, **kwargs) -> _FakeContext:
        return self._context


class _FakePlaywright:
    def __init__(self, context: _FakeContext) -> None:
        self.chromium = _FakeChromium(context)


class _FakeSyncPlaywright:
    def __init__(self, playwright) -> None:
        self._playwright = playwright

    def __enter__(self):
        return self._playwright

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class SignInTests(unittest.TestCase):
    def test_run_browser_sign_in_returns_message_then_status_on_success(self) -> None:
        attendance_payload = {
            "data": {
                "calendar": [
                    {"available": True, "done": False},
                    {"available": False, "done": False},
                ]
            }
        }
        refreshed_payload = {
            "data": {
                "calendar": [
                    {"available": False, "done": True},
                    {"available": False, "done": False},
                ]
            }
        }
        fake_page = _FakePage(
            [
                _FakeResponse(200, attendance_payload, method="GET"),
                _FakeResponse(200, {}, ok=True, method="POST"),
                _FakeResponse(200, refreshed_payload, method="GET"),
            ]
        )
        fake_context = _FakeContext(fake_page)

        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "browser-profile"
            profile_dir.mkdir()
            with patch("sign_in.click_day_tile"), patch(
                "playwright.sync_api.sync_playwright",
                return_value=_FakeSyncPlaywright(_FakePlaywright(fake_context)),
            ):
                message, status = sign_in.run_browser_sign_in(
                    profile_dir=profile_dir,
                    signin_url="https://example.com",
                    headless=True,
                    browser_channel="",
                    timeout_seconds=1,
                )

        self.assertEqual(status, SUCCESS)
        self.assertIn("Day 1", message)

    def test_main_reports_state_file_errors_separately(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "timezone": "Asia/Taipei",
                        "state_path": "./state.json",
                        "log_dir": "./logs",
                        "browser_profile_dir": "./browser-profile",
                    }
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with patch.object(
                sign_in,
                "parse_args",
                return_value=Namespace(config=str(config_path), dry_run=False, force=False),
            ), patch.object(sign_in, "load_timezone", return_value=timezone.utc), patch.object(
                sign_in, "load_state", side_effect=StateFileError("broken state")
            ), redirect_stderr(stderr):
                exit_code = sign_in.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("State file error", stderr.getvalue())

    def test_main_reports_timezone_errors_as_configuration_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "timezone": "Asia/Taipei",
                        "state_path": "./state.json",
                        "log_dir": "./logs",
                        "browser_profile_dir": "./browser-profile",
                    }
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with patch.object(
                sign_in,
                "parse_args",
                return_value=Namespace(config=str(config_path), dry_run=False, force=False),
            ), patch.object(sign_in, "load_timezone", side_effect=RuntimeError("bad timezone")), redirect_stderr(stderr):
                exit_code = sign_in.main()

        self.assertEqual(exit_code, 30)
        self.assertIn("Configuration error", stderr.getvalue())

    def test_main_reports_interaction_errors_as_runtime_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "settings.json"
            config_path.write_text(
                json.dumps(
                    {
                        "timezone": "Asia/Taipei",
                        "state_path": "./state.json",
                        "log_dir": "./logs",
                        "browser_profile_dir": "./browser-profile",
                    }
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with patch.object(
                sign_in,
                "parse_args",
                return_value=Namespace(config=str(config_path), dry_run=False, force=True),
            ), patch.object(sign_in, "load_timezone", return_value=timezone.utc), patch.object(
                sign_in,
                "run_browser_sign_in",
                side_effect=InteractionError("could not click tile"),
            ), redirect_stderr(stderr):
                exit_code = sign_in.main()

        self.assertEqual(exit_code, 10)
        self.assertIn("Runtime error", stderr.getvalue())

    def test_page_looks_logged_out_does_not_treat_account_text_as_login(self) -> None:
        page = _FakePage([])
        page.body_text = "Open account settings"
        page.login_form_count = 0

        self.assertFalse(sign_in.page_looks_logged_out(page))


if __name__ == "__main__":
    unittest.main()
