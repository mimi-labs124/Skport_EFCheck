# Release Guide

## Scope

This document covers GitHub-facing release preparation for EFCheck.

## Release naming

Recommended naming:

- tag: `v0.2.0`
- title: `v0.2.0 - Unified CLI and Windows packaging`

## Versioning strategy

Use `major.minor.patch`.

- Patch: bug fixes, docs-only corrections, release-script fixes
- Minor: new commands, new wrappers, packaging improvements, non-breaking config evolution
- Major: breaking config layout or CLI compatibility changes

## Suggested GitHub repository metadata

Description:

`Windows-first unofficial SKPORT sign-in helper for Endfield and Arknights with Playwright session capture, local scheduling, and packaged builds.`

Topics:

- `python`
- `playwright`
- `windows`
- `automation`
- `task-scheduler`
- `pyinstaller`
- `endfield`
- `arknights`

## Pre-release checklist

- Run `python -m unittest discover -s tests -v`
- Run `python -m ruff check .`
- Build `onedir`
- Build `onefile`
- Build release zips
- Confirm release archives contain:
  - executable output
  - wrappers
  - `README.md`
  - `README.zh-TW.md`
  - `LICENSE`
  - `SECURITY.md`
  - `config/settings.example.json`

## Notes for release descriptions

Always state:

- the project is unofficial
- source mode and packaged mode are both supported
- onefile still requires external Playwright browser bootstrap
- browser/session data remains local and should never be published
