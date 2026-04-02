from __future__ import annotations

import json

from efcheck.runtime import RuntimeContext


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "paths",
        help="Show the resolved EFCheck data and config paths.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the resolved paths as JSON.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    paths = runtime.app_paths.as_serializable_dict()
    if args.json:
        runtime.stdout.write(json.dumps(paths, ensure_ascii=True, indent=2) + "\n")
        return 0

    for key, value in paths.items():
        runtime.stdout.write(f"{key}: {value}\n")
    return 0
