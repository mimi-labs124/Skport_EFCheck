# Changelog

All notable changes to EFCheck will be documented in this file.

The format is based on Keep a Changelog and uses a simple `major.minor.patch` versioning scheme.

## [0.2.0] - 2026-04-03

### Added

- Python package metadata with `efcheck` console entry point
- Unified CLI with `run`, `capture-session`, `configure-sites`, `register-task`, `doctor`, `paths`, `package onedir`, and `package onefile`
- Centralized source-mode vs packaged-mode path resolution
- Config initialization and doctor commands
- PyInstaller build helpers and Windows packaging scripts
- Release and packaging documentation
- Additional tests for paths, CLI, doctor, packaging, and release docs

### Changed

- Moved core runtime behavior behind package command modules
- Converted root Python entry scripts into thin legacy shims
- Updated batch wrappers to prefer `efcheck.exe` and otherwise call `python -m efcheck`
- Updated task registration to schedule the unified CLI run path
- Improved repo documentation for source mode, packaged mode, and sensitive data handling
