from __future__ import annotations

from efcheck.default_settings import write_default_settings
from efcheck.runtime import RuntimeContext


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "init",
        help="Create the local EFCheck config file if it does not exist.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing settings.json file.",
    )
    parser.add_argument(
        "--include-arknights",
        action="store_true",
        help="Write a default config that includes the Arknights site entry.",
    )
    parser.add_argument(
        "--share-arknights-profile",
        action="store_true",
        help="Use the same browser profile path for Endfield and Arknights.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    config_path = write_default_settings(
        runtime.app_paths,
        include_arknights=args.include_arknights,
        share_arknights_profile=args.share_arknights_profile,
        force=args.force,
    )
    runtime.stdout.write(f"Initialized config at {config_path}\n")
    return 0
