from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TextIO

from skport_signin.app_paths import AppPaths, build_app_paths


@dataclass
class RuntimeContext:
    app_paths: AppPaths
    stdout: TextIO
    stderr: TextIO


def build_runtime_context(
    *,
    config_override: str | None = None,
    base_dir_override: str | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> RuntimeContext:
    return RuntimeContext(
        app_paths=build_app_paths(
            config_override=config_override,
            base_dir_override=base_dir_override,
        ),
        stdout=stdout or sys.stdout,
        stderr=stderr or sys.stderr,
    )


