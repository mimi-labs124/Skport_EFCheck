@echo off
setlocal
cd /d "%~dp0"

set "NO_PAUSE="
if /I "%~1"=="--no-pause" (
  set "NO_PAUSE=1"
)

where py >nul 2>nul
if errorlevel 1 (
  set "PYTHON_CMD=python"
) else (
  set "PYTHON_CMD=py -3"
)

if exist ".\skport_signin.exe" (
  set "SKPORT_SIGNIN_CMD=.\skport_signin.exe"
) else (
  if not exist ".venv\Scripts\python.exe" (
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 exit /b 1
  )

  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 exit /b 1
  ".venv\Scripts\python.exe" -m pip install -e .
  if errorlevel 1 exit /b 1

  set "SKPORT_SIGNIN_CMD=.venv\Scripts\python.exe -m skport_signin"
)

%SKPORT_SIGNIN_CMD% init
if errorlevel 1 exit /b 1
%SKPORT_SIGNIN_CMD% doctor --install-browser
if errorlevel 1 exit /b 1

echo Setup complete.
echo Next: run capture_session.bat
if not defined NO_PAUSE (
  pause
)
endlocal
