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

if not exist ".venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
playwright install chromium
if errorlevel 1 exit /b 1

if not exist "config\settings.json" (
  copy /Y "config\settings.example.json" "config\settings.json" >nul
  if errorlevel 1 exit /b 1
)

echo Setup complete.
echo Next: run capture_session.bat
if not defined NO_PAUSE (
  pause
)
endlocal
