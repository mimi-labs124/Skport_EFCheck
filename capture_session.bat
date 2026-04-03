@echo off
setlocal
cd /d "%~dp0"

if exist ".\skport_signin.exe" (
  ".\skport_signin.exe" capture-session %*
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m skport_signin capture-session %*
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m skport_signin capture-session %*
  ) else (
    py -3 -m skport_signin capture-session %*
  )
)
pause
endlocal
