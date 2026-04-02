from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from efcheck.runtime import RuntimeContext

DEFAULT_TASK_NAME = "EFCheck Sign-In"


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "register-task",
        help="Register the Windows logon scheduled task.",
    )
    parser.add_argument(
        "--task-name",
        default=DEFAULT_TASK_NAME,
        help="Task Scheduler task name.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=90,
        help="Random logon delay for the scheduled task.",
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Suppress the wrapper pause in the PowerShell registration script.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        runtime.stderr.write("Missing dependency: PowerShell was not found on PATH.\n")
        return 20

    script_path = find_registration_script(runtime)
    if not script_path.exists():
        runtime.stderr.write(f"Missing file: {script_path}\n")
        return 30

    command = [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
        "-TaskName",
        args.task_name,
        "-DelaySeconds",
        str(args.delay_seconds),
    ]
    if args.no_pause:
        command.append("-NoPause")

    result = subprocess.run(command, check=False)
    return result.returncode


def find_registration_script(runtime: RuntimeContext) -> Path:
    bundle_candidate = runtime.app_paths.bundle_root / "register_logon_task.ps1"
    if bundle_candidate.exists():
        return bundle_candidate
    return runtime.app_paths.resource_root / "register_logon_task.ps1"
