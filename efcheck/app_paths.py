from __future__ import annotations

import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

APP_NAME = "EFCheck"
BASE_DIR_ENV = "EFCHECK_BASE_DIR"
CONFIG_PATH_ENV = "EFCHECK_CONFIG"


@dataclass(frozen=True)
class AppPaths:
    mode: str
    bundle_root: Path
    resource_root: Path
    executable_path: Path
    base_dir: Path
    config_dir: Path
    config_file: Path
    state_dir: Path
    logs_dir: Path
    runtime_dir: Path
    browser_profiles_dir: Path
    playwright_browsers_dir: Path

    def as_serializable_dict(self) -> dict[str, str]:
        return {
            key: str(value) if isinstance(value, Path) else value
            for key, value in asdict(self).items()
        }


def is_packaged_mode() -> bool:
    return bool(getattr(sys, "frozen", False))


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_packaged_base_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / "AppData" / "Local" / APP_NAME


def build_app_paths(
    *,
    config_override: str | None = None,
    base_dir_override: str | None = None,
) -> AppPaths:
    packaged = is_packaged_mode()
    bundle_root = Path(sys.executable).resolve().parent if packaged else project_root()
    resource_root = Path(getattr(sys, "_MEIPASS", bundle_root)).resolve()

    base_dir_value = base_dir_override or os.environ.get(BASE_DIR_ENV)
    if base_dir_value:
        base_dir = Path(base_dir_value).expanduser().resolve()
    else:
        base_dir = default_packaged_base_dir().resolve() if packaged else bundle_root

    config_value = config_override or os.environ.get(CONFIG_PATH_ENV)
    if config_value:
        config_file = Path(config_value).expanduser().resolve()
    else:
        config_file = (base_dir / "config" / "settings.json").resolve()

    config_dir = config_file.parent
    return AppPaths(
        mode="packaged" if packaged else "source",
        bundle_root=bundle_root,
        resource_root=resource_root,
        executable_path=Path(sys.executable).resolve(),
        base_dir=base_dir,
        config_dir=config_dir,
        config_file=config_file,
        state_dir=(base_dir / "state").resolve(),
        logs_dir=(base_dir / "logs").resolve(),
        runtime_dir=(base_dir / "runtime").resolve(),
        browser_profiles_dir=(base_dir / "browser-profile").resolve(),
        playwright_browsers_dir=(base_dir / "runtime" / "playwright-browsers").resolve(),
    )
