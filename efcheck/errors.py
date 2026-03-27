from __future__ import annotations


class ConfigError(ValueError):
    pass


class StateFileError(RuntimeError):
    pass


class InteractionError(RuntimeError):
    pass
