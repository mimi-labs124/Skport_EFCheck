from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from efcheck.errors import ConfigError


@dataclass(frozen=True)
class RuntimeSettings:
    timezone: str
    signin_url: str
    state_path: str
    log_dir: str
    browser_profile_dir: str
    browser_channel: str
    headless: bool
    timeout_seconds: int
    max_attempts_per_day: int


def load_runtime_settings(config_path: Path, default_url: str) -> RuntimeSettings:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Could not parse config file at {config_path}: {exc.msg}.") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Configuration file at {config_path} must contain a JSON object.")

    return RuntimeSettings(
        timezone=_parse_string(data.get("timezone", "Asia/Taipei"), field_name="timezone"),
        signin_url=_parse_string(data.get("signin_url", default_url), field_name="signin_url"),
        state_path=_parse_string(data.get("state_path", "../state/last_run.json"), field_name="state_path"),
        log_dir=_parse_string(data.get("log_dir", "../logs"), field_name="log_dir"),
        browser_profile_dir=_parse_string(
            data.get("browser_profile_dir", "../state/browser-profile"),
            field_name="browser_profile_dir",
        ),
        browser_channel=_parse_string(data.get("browser_channel", ""), field_name="browser_channel"),
        headless=_parse_bool(data.get("headless", True), field_name="headless"),
        timeout_seconds=_parse_int(data.get("timeout_seconds", 20), field_name="timeout_seconds"),
        max_attempts_per_day=_parse_int(
            data.get("max_attempts_per_day", 2),
            field_name="max_attempts_per_day",
        ),
    )


def resolve_path(config_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (config_path.parent / candidate).resolve()


def _parse_string(value: object, *, field_name: str) -> str:
    if isinstance(value, str):
        return value
    raise ConfigError(f"{field_name} must be a string, not {value!r}.")


def _parse_bool(value: object, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ConfigError(f"{field_name} must be true or false, not {value!r}.")


def _parse_int(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{field_name} must be an integer, not {value!r}.")
    return value
