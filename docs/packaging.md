# Packaging Guide

## Overview

Skport_Signin supports two Windows packaging targets:

- `onedir`: preferred for reliability
- `onefile`: convenient distribution with slower startup

Both are built from the same package code and the same PyInstaller spec.
Use the packaging commands from a source checkout, not from a packaged executable.

## Build commands

### onedir

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build_onedir.ps1
```

### onefile

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build_onefile.ps1
```

### release archives

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\package_release.ps1
```

This script also writes `dist/releases/Skport_Signin-SHA256.txt` for the generated release assets.

## Output layout

Build output roots:

- `dist/pyinstaller/onedir`
- `dist/pyinstaller/onefile`
- `dist/releases`

Release archives flatten the executable output so the wrappers can find `skport_signin.exe` in the release root.

## Browser runtime strategy

The packaged executable does not try to embed a full Chromium browser payload into the binary.

Instead:

- on first use, run `skport_signin doctor --install-browser`
- packaged mode writes browser runtime data under `%LOCALAPPDATA%\\Skport_Signin\\runtime\\playwright-browsers`

This keeps the packaging model deterministic and avoids shipping a fragile, oversized executable that still depends on runtime extraction.

## Data directories in packaged mode

Packaged mode uses `%LOCALAPPDATA%\\Skport_Signin` by default:

- `config/`
- `state/`
- `logs/`
- `runtime/`
- `browser-profile/`

## PyInstaller notes

- The spec includes `playwright`, `tzdata`, `config/settings.example.json`, and `register_logon_task.ps1`
- The batch wrappers remain outside the executable and are included in release archives
- onefile mode is supported as a CLI distribution, not as a fully self-contained browser payload


## CI smoke coverage

GitHub Actions runs a Windows **onedir** packaging smoke build.

It verifies:

- `python -m skport_signin package onedir` can start and complete
- `dist/pyinstaller/onedir/skport_signin/skport_signin.exe` exists
- the packaged executable can run `--help`

`onefile` is intentionally excluded from CI smoke to keep runtime and extraction overhead reasonable.

