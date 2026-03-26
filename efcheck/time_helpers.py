from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def load_timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(
            f"Time zone '{name}' is unavailable on this machine. "
            "Install the `tzdata` package or run `python -m pip install -r requirements.txt`."
        ) from exc
