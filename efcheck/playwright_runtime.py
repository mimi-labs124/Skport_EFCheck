from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

from efcheck.app_paths import AppPaths


@contextmanager
def playwright_browser_env(paths: AppPaths):
    if paths.mode != "packaged":
        yield
        return

    original = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(paths.playwright_browsers_dir)
    try:
        yield
    finally:
        if original is None:
            os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
        else:
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = original


def ensure_browser_runtime_available(playwright, paths: AppPaths) -> Path:
    browser_executable = Path(playwright.chromium.executable_path)
    if browser_executable.exists():
        return browser_executable

    if paths.mode == "packaged":
        raise FileNotFoundError(
            "Playwright Chromium is not installed for packaged mode. "
            "Run `efcheck doctor --install-browser` first."
        )

    raise FileNotFoundError(
        "Playwright Chromium is not installed. "
        "Run `playwright install chromium` or "
        "`python -m efcheck doctor --install-browser`."
    )
