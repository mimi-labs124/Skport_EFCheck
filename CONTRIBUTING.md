# Contributing

EFCheck is primarily a Windows automation tool. Contributions should preserve Windows stability first, then source-mode maintainability, then packaging convenience.

## Local development

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Optional browser bootstrap for manual testing:

```powershell
python -m efcheck doctor --install-browser
```

## Test commands

Run all tests:

```powershell
python -m unittest discover -s tests -v
```

Run lint:

```powershell
python -m ruff check .
```

## Packaging

Build onedir:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build_onedir.ps1
```

Build onefile:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build_onefile.ps1
```

Package release archives:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\package_release.ps1
```

## Rules for changes

- Do not commit local `state/`, `logs/`, or real `config/settings.json`
- Keep wrappers and CLI behavior aligned
- Add or update tests for behavioral changes
- Prefer mode-aware helpers instead of scattering source-vs-packaged checks
- Document user-visible changes in `README.md`, `README.zh-TW.md`, and `CHANGELOG.md`
