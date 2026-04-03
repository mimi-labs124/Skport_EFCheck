from __future__ import annotations

from argparse import Namespace

from skport_signin.commands import capture_session as capture_session_command
from skport_signin.commands import configure_sites as configure_sites_command
from skport_signin.commands import register_task as register_task_command
from skport_signin.runtime import RuntimeContext

DEFAULT_REGISTER_DELAY_SECONDS = 90


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser(
        "setup",
        help="Run the guided interactive setup flow.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run the guided setup prompts.",
    )
    parser.set_defaults(handler=handle_command)


def handle_command(args, runtime: RuntimeContext) -> int:
    return run_setup(runtime=runtime)


def run_setup(*, runtime: RuntimeContext) -> int:
    config_path = runtime.app_paths.config_file
    existing_enabled = configure_sites_command.existing_enabled_sites(config_path)

    enable_endfield = prompt_yes_no(
        runtime,
        "Enable Endfield sign-in?",
        default="endfield" in existing_enabled,
    )
    enable_arknights = prompt_yes_no(
        runtime,
        "Enable Arknights sign-in?",
        default="arknights" in existing_enabled,
    )

    if not enable_endfield and not enable_arknights:
        runtime.stdout.write("No site selected. Defaulting to Endfield enabled.\n")
        enable_endfield = True

    enabled_sites: set[str] = set()
    if enable_endfield:
        enabled_sites.add("endfield")
    if enable_arknights:
        enabled_sites.add("arknights")

    share_profile_with_arknights = False
    if enable_endfield and enable_arknights:
        share_profile_with_arknights = prompt_yes_no(
            runtime,
            "Share Endfield browser profile with Arknights?",
            default=False,
        )

    configure_sites_command.configure_sites(
        config_path,
        runtime=runtime,
        enabled_sites=enabled_sites,
        share_profile_with_arknights=share_profile_with_arknights,
    )
    runtime.stdout.write(f"Configured sites in {config_path}\n")

    if prompt_yes_no(runtime, "Capture your sign-in session now?", default=False):
        if enable_endfield:
            exit_code = capture_session_command.run_capture_session(
                runtime=runtime,
                site_name="endfield",
            )
            if exit_code != 0:
                return exit_code

        if enable_arknights:
            runtime.stdout.write(
                "Continue with the Arknights page in the same guided capture flow.\n"
            )
            exit_code = capture_session_command.run_capture_session(
                runtime=runtime,
                site_name="arknights",
            )
            if exit_code != 0:
                return exit_code

    if prompt_yes_no(runtime, "Register the Windows logon scheduled task now?", default=False):
        exit_code = register_task_command.handle_command(
            Namespace(
                task_name=register_task_command.DEFAULT_TASK_NAME,
                delay_seconds=DEFAULT_REGISTER_DELAY_SECONDS,
                no_pause=True,
            ),
            runtime,
        )
        if exit_code != 0:
            return exit_code

    runtime.stdout.write("Skport_Signin setup flow finished.\n")
    runtime.stdout.write(
        "Manual tools remain available: "
        "capture_session.bat, run_signin.bat, register_logon_task.bat\n"
    )
    return 0


def prompt_yes_no(runtime: RuntimeContext, message: str, *, default: bool) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        runtime.stdout.write(f"{message} {suffix}:")
        response = input().strip().casefold()
        if not response:
            return default
        if response in {"y", "yes"}:
            return True
        if response in {"n", "no"}:
            return False
        runtime.stdout.write("Please answer Y or N.\n")
