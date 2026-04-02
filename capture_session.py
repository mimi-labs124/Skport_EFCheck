from __future__ import annotations

import argparse
from pathlib import Path
import sys

from efcheck.config import DEFAULT_ENDFIELD_KEY, find_site, load_runtime_settings, resolve_path
from efcheck.errors import ConfigError


DEFAULT_CONFIG = Path("config/settings.json")
DEFAULT_URL = "https://game.skport.com/endfield/sign-in?header=0&hg_media=skport&hg_link_campaign=tools"


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    try:
        settings = load_runtime_settings(config_path, DEFAULT_URL)
        site = find_site(settings, args.site)
        profile_dir = resolve_path(config_path, site.browser_profile_dir)
        signin_url = site.signin_url
        channel = settings.browser_channel

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            print(
                "Missing dependency: playwright is not installed. "
                "Run `python -m pip install playwright` and then `playwright install chromium`.",
                file=sys.stderr,
            )
            return 20

        profile_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                str(profile_dir),
                channel=channel or None,
                headless=False,
                viewport={"width": 1440, "height": 1200},
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(signin_url, wait_until="domcontentloaded")
            input(
                "Log in in the opened browser window. When the page shows your sign-in dashboard, press Enter here to save the session."
            )
            context.close()
        print(f"Saved browser session in {profile_dir}")
        return 0
    except FileNotFoundError as exc:
        print(f"Missing file: {exc}", file=sys.stderr)
        return 30
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a browser session for EFCheck.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to settings.json")
    parser.add_argument(
        "--site",
        default=DEFAULT_ENDFIELD_KEY,
        help="Site key or name to capture a session for.",
    )
    return parser.parse_args()

if __name__ == "__main__":
    raise SystemExit(main())
