from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from efcheck.default_settings import build_default_settings
from efcheck.errors import ConfigError
from efcheck.runtime import RuntimeContext, build_runtime_context


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "configure-sites",
        help="Rewrite the configured sites in settings.json.",
    )
    parser.add_argument(
        "--include-arknights",
        action="store_true",
        help="Enable the Arknights sign-in site entry.",
    )
    parser.add_argument(
        "--share-arknights-profile",
        action="store_true",
        help="Share the Endfield browser profile with Arknights.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    configure_sites(
        runtime.app_paths.config_file,
        runtime=runtime,
        include_arknights=args.include_arknights,
        share_profile_with_arknights=args.share_arknights_profile,
    )
    runtime.stdout.write(f"Configured sites in {runtime.app_paths.config_file}\n")
    return 0


def configure_sites(
    config_path: Path,
    *,
    runtime: RuntimeContext | None = None,
    include_arknights: bool,
    share_profile_with_arknights: bool,
) -> None:
    runtime = runtime or build_runtime_context(config_override=str(config_path))
    data = _load_existing_config(config_path)
    defaults = build_default_settings(
        runtime.app_paths,
        include_arknights=include_arknights,
        share_arknights_profile=share_profile_with_arknights,
    )
    data["sites"] = defaults["sites"]

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _load_existing_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}

    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file at {config_path} must contain a JSON object.")
    return {
        key: value
        for key, value in data.items()
        if key
        in {
            "timezone",
            "log_dir",
            "browser_channel",
            "headless",
            "timeout_seconds",
            "max_attempts_per_day",
        }
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure EFCheck sites for guided setup.")
    parser.add_argument("--config", default="config/settings.json", help="Path to settings.json")
    parser.add_argument(
        "--include-arknights",
        action="store_true",
        help="Add the Arknights SKPORT sign-in page to the configured sites.",
    )
    parser.add_argument(
        "--share-arknights-profile",
        action="store_true",
        help="Use the same browser profile directory for Endfield and Arknights.",
    )
    return parser.parse_args(argv)


def legacy_main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runtime = build_runtime_context(config_override=args.config)
    try:
        configure_sites(
            runtime.app_paths.config_file,
            runtime=runtime,
            include_arknights=args.include_arknights,
            share_profile_with_arknights=args.share_arknights_profile,
        )
    except FileNotFoundError as exc:
        print(f"Missing file: {exc}", file=sys.stderr)
        return 30
    except (ConfigError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 30

    print("Configured EFCheck sites.")
    return 0


main = legacy_main
