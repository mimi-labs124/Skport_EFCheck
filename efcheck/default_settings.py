from __future__ import annotations

import json
from pathlib import Path

from efcheck.app_paths import AppPaths

ENDFIELD_SIGNIN_URL = "https://game.skport.com/endfield/sign-in?header=0&hg_media=skport&hg_link_campaign=tools"
ARKNIGHTS_SIGNIN_URL = "https://game.skport.com/arknights/sign-in"


def build_default_settings(
    paths: AppPaths,
    *,
    include_arknights: bool = False,
    share_arknights_profile: bool = False,
) -> dict:
    settings = {
        "timezone": "Asia/Taipei",
        "log_dir": "../logs",
        "browser_channel": "",
        "headless": True,
        "timeout_seconds": 20,
        "max_attempts_per_day": 2,
        "sites": [
            {
                "key": "endfield",
                "name": "Endfield",
                "enabled": True,
                "signin_url": ENDFIELD_SIGNIN_URL,
                "attendance_path": "/web/v1/game/endfield/attendance",
                "state_path": "../state/endfield-last_run.json",
                "browser_profile_dir": default_endfield_profile_dir(paths),
            }
        ],
    }

    if include_arknights:
        settings["sites"].append(
            {
                "key": "arknights",
                "name": "Arknights",
                "enabled": True,
                "signin_url": ARKNIGHTS_SIGNIN_URL,
                "attendance_path": "/api/v1/game/attendance",
                "state_path": "../state/arknights-last_run.json",
                "browser_profile_dir": default_arknights_profile_dir(
                    paths,
                    share_profile=share_arknights_profile,
                ),
            }
        )

    return settings


def write_default_settings(
    paths: AppPaths,
    *,
    config_path: Path | None = None,
    include_arknights: bool = False,
    share_arknights_profile: bool = False,
    force: bool = False,
) -> Path:
    target_path = config_path or paths.config_file
    if target_path.exists() and not force:
        return target_path

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(
            build_default_settings(
                paths,
                include_arknights=include_arknights,
                share_arknights_profile=share_arknights_profile,
            ),
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target_path


def default_endfield_profile_dir(paths: AppPaths) -> str:
    if paths.mode == "packaged":
        return "../browser-profile/endfield"
    return "../state/browser-profile"


def default_arknights_profile_dir(paths: AppPaths, *, share_profile: bool) -> str:
    if share_profile:
        return default_endfield_profile_dir(paths)
    if paths.mode == "packaged":
        return "../browser-profile/arknights"
    return "../state/arknights-browser-profile"
