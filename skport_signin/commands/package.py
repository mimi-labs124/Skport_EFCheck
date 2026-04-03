from __future__ import annotations

from pathlib import Path

from skport_signin.packaging.pyinstaller_helpers import build_pyinstaller
from skport_signin.runtime import RuntimeContext


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "package",
        help="Build Windows packaging artifacts.",
    )
    package_subparsers = parser.add_subparsers(dest="package_mode", required=True)

    for mode in ("onedir", "onefile"):
        mode_parser = package_subparsers.add_parser(mode, help=f"Build the {mode} Windows package.")
        mode_parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    if runtime.app_paths.mode != "source":
        runtime.stderr.write(
            "Packaging is only supported from a source checkout. "
            "Use the repository's packaging scripts instead of a packaged executable.\n"
        )
        return 20

    project_root = runtime.app_paths.bundle_root
    dist_dir = build_pyinstaller(args.package_mode, Path(project_root))
    runtime.stdout.write(f"Built {args.package_mode} package in {dist_dir}\n")
    return 0


