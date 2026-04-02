@echo off
setlocal
cd /d "%~dp0"

if exist ".\efcheck.exe" (
  ".\efcheck.exe" run %*
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m efcheck run %*
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m efcheck run %*
  ) else (
    py -3 -m efcheck run %*
  )
)
endlocal
