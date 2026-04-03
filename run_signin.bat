@echo off
setlocal
cd /d "%~dp0"

if exist ".\skport_signin.exe" (
  ".\skport_signin.exe" run %*
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m skport_signin run %*
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m skport_signin run %*
  ) else (
    py -3 -m skport_signin run %*
  )
)
endlocal

