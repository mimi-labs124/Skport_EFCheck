from __future__ import annotations

import argparse
from typing import Sequence, TextIO

from efcheck.commands import capture_session as capture_session_command
from efcheck.commands import configure_sites as configure_sites_command
from efcheck.commands import doctor as doctor_command
from efcheck.commands import init as init_command
from efcheck.commands import package as package_command
from efcheck.commands import paths as paths_command
from efcheck.commands import register_task as register_task_command
from efcheck.commands import run as run_command
from efcheck.errors import ConfigError, InteractionError, StateFileError
from efcheck.runtime import build_runtime_context

COMMAND_HELP = {
    "run": "Run sign-in for all enabled sites.",
    "capture-session": "Open a browser and save a login session profile.",
    "configure-sites": "Configure the enabled SKPORT sites in settings.json.",
    "register-task": "Register the Windows logon scheduled task.",
    "doctor": "Check config, browser runtime, and environment health.",
    "init": "Create or refresh a default local config file.",
    "paths": "Show resolved config/data paths.",
    "package": "Build Windows packaging artifacts.",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="efcheck",
        description="EFCheck unified CLI for source and packaged Windows workflows.",
    )
    parser.add_argument(
        "--config",
        help="Explicit path to settings.json.",
    )
    parser.add_argument(
        "--base-dir",
        help="Override the EFCheck data directory root.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    run_command.register_parser(subparsers)
    capture_session_command.register_parser(subparsers)
    configure_sites_command.register_parser(subparsers)
    register_task_command.register_parser(subparsers)

    doctor_command.register_parser(subparsers)
    init_command.register_parser(subparsers)
    paths_command.register_parser(subparsers)

    package_command.register_parser(subparsers)

    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = build_runtime_context(
        config_override=args.config,
        base_dir_override=args.base_dir,
        stdout=stdout,
        stderr=stderr,
    )
    try:
        return args.handler(args, runtime)
    except FileNotFoundError as exc:
        runtime.stderr.write(f"Missing file: {exc}\n")
        return 30
    except ConfigError as exc:
        runtime.stderr.write(f"Configuration error: {exc}\n")
        return 30
    except StateFileError as exc:
        runtime.stderr.write(f"State file error: {exc}\n")
        return 30
    except InteractionError as exc:
        runtime.stderr.write(f"Runtime error: {exc}\n")
        return 10
    except ImportError as exc:
        runtime.stderr.write(f"Missing dependency: {exc}\n")
        return 20


def _not_implemented(name: str):
    def handler(args, runtime) -> int:
        runtime.stderr.write(f"{name} is not implemented yet.\n")
        return 2

    return handler
