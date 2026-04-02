@echo off
setlocal
cd /d "%~dp0"

if exist ".\efcheck.exe" (
  ".\efcheck.exe" capture-session %*
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m efcheck capture-session %*
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m efcheck capture-session %*
  ) else (
    py -3 -m efcheck capture-session %*
  )
)
pause
endlocal
