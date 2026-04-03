from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from skport_signin.playwright_runtime import playwright_browser_env
from skport_signin.runtime import RuntimeContext


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "doctor",
        help="Validate config, paths, and browser runtime availability.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the doctor report as JSON.",
    )
    parser.add_argument(
        "--install-browser",
        action="store_true",
        help="Install the Playwright Chromium runtime into the SKPORT Sign-in runtime directory.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    if args.install_browser:
        install_browser_runtime(runtime)

    report = build_doctor_report(runtime)
    if args.json:
        runtime.stdout.write(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
        return 0

    runtime.stdout.write(f"Mode: {report['mode']}\n")
    runtime.stdout.write(f"Config file: {report['paths']['config_file']}\n")
    runtime.stdout.write(f"Config exists: {report['config_exists']}\n")
    runtime.stdout.write(f"Playwright importable: {report['playwright_importable']}\n")
    runtime.stdout.write(f"Browser runtime installed: {report['browser_runtime_installed']}\n")
    runtime.stdout.write(f"Browser executable: {report['browser_executable'] or 'missing'}\n")
    return 0


def build_doctor_report(runtime: RuntimeContext) -> dict[str, Any]:
    browser_executable = None
    playwright_importable = False
    browser_runtime_installed = False

    try:
        browser_executable = resolve_browser_executable(runtime)
        playwright_importable = True
        browser_runtime_installed = bool(browser_executable and Path(browser_executable).exists())
    except ImportError:
        playwright_importable = False

    return {
        "mode": runtime.app_paths.mode,
        "config_exists": runtime.app_paths.config_file.exists(),
        "playwright_importable": playwright_importable,
        "browser_runtime_installed": browser_runtime_installed,
        "browser_executable": browser_executable,
        "paths": runtime.app_paths.as_serializable_dict(),
    }


def resolve_browser_executable(runtime: RuntimeContext) -> str | None:
    with playwright_browser_env(runtime.app_paths):
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            return playwright.chromium.executable_path


def install_browser_runtime(runtime: RuntimeContext) -> None:
    runtime.app_paths.playwright_browsers_dir.mkdir(parents=True, exist_ok=True)
    original_argv = sys.argv[:]
    try:
        with playwright_browser_env(runtime.app_paths):
            import playwright.__main__

            sys.argv = ["playwright", "install", "chromium"]
            playwright.__main__.main()
    finally:
        sys.argv = original_argv


