from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from uuid import uuid4

from skport_signin.config import load_runtime_settings, resolve_path
from skport_signin.default_settings import KNOWN_SITES
from skport_signin.errors import ConfigError
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
    runtime.stdout.write(f"Config valid: {report['config_valid']}\n")
    if report["config_error"]:
        runtime.stdout.write(f"Config error: {report['config_error']}\n")
    enabled_sites_text = ", ".join(report["enabled_sites"]) if report["enabled_sites"] else "none"
    runtime.stdout.write(
        f"Enabled sites: {enabled_sites_text}\n"
    )
    runtime.stdout.write(f"Playwright importable: {report['playwright_importable']}\n")
    runtime.stdout.write(f"Browser runtime installed: {report['browser_runtime_installed']}\n")
    runtime.stdout.write(f"Browser executable: {report['browser_executable'] or 'missing'}\n")
    for name, check in report["path_checks"].items():
        runtime.stdout.write(
            f"Path {name}: exists={check['exists']} writable={check['writable']} "
            f"path={check['path']}\n"
        )
    for site in report["sites"]:
        runtime.stdout.write(
            f"Site {site['key']}: enabled={site['enabled']} "
            f"profile_exists={site['profile_dir_exists']} "
            f"state_exists={site['state_file_exists']}\n"
        )
    return 0


def build_doctor_report(runtime: RuntimeContext) -> dict[str, Any]:
    config_valid = False
    config_error = None
    enabled_sites: list[str] = []
    sites: list[dict[str, Any]] = []
    if runtime.app_paths.config_file.exists():
        try:
            settings = load_runtime_settings(
                runtime.app_paths.config_file,
                KNOWN_SITES[0].signin_url,
            )
        except ConfigError as exc:
            config_error = str(exc)
        else:
            config_valid = True
            enabled_sites = [site.key for site in settings.sites if site.enabled]
            sites = [
                build_site_report(runtime, site)
                for site in settings.sites
            ]
    else:
        config_error = f"Config file does not exist at {runtime.app_paths.config_file}."

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
        "config_valid": config_valid,
        "config_error": config_error,
        "enabled_sites": enabled_sites,
        "sites": sites,
        "playwright_importable": playwright_importable,
        "browser_runtime_installed": browser_runtime_installed,
        "browser_executable": browser_executable,
        "path_checks": build_path_checks(runtime),
        "paths": runtime.app_paths.as_serializable_dict(),
    }


def build_site_report(runtime: RuntimeContext, site) -> dict[str, Any]:
    config_path = runtime.app_paths.config_file
    state_path = resolve_path(config_path, site.state_path)
    profile_dir = resolve_path(config_path, site.browser_profile_dir)
    return {
        "key": site.key,
        "name": site.name,
        "enabled": site.enabled,
        "signin_url": site.signin_url,
        "attendance_path": site.attendance_path,
        "state_path": str(state_path),
        "state_file_exists": state_path.exists(),
        "profile_dir": str(profile_dir),
        "profile_dir_exists": profile_dir.exists(),
    }


def build_path_checks(runtime: RuntimeContext) -> dict[str, dict[str, Any]]:
    return {
        "config_dir": probe_directory(runtime.app_paths.config_dir),
        "state_dir": probe_directory(runtime.app_paths.state_dir),
        "logs_dir": probe_directory(runtime.app_paths.logs_dir),
        "runtime_dir": probe_directory(runtime.app_paths.runtime_dir),
        "browser_profiles_dir": probe_directory(runtime.app_paths.browser_profiles_dir),
        "playwright_browsers_dir": probe_directory(runtime.app_paths.playwright_browsers_dir),
    }


def probe_directory(path: Path) -> dict[str, Any]:
    existed = path.exists()
    writable = False
    error = None
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe_path = path / f".doctor-probe-{uuid4().hex}.tmp"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink()
        writable = True
    except Exception as exc:
        error = str(exc)

    return {
        "path": str(path),
        "exists": existed,
        "writable": writable,
        "error": error,
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
