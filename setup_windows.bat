@echo off
setlocal
cd /d "%~dp0"

set "NO_PAUSE="
set "VENV_PY=.venv\Scripts\python.exe"
set "PYTHON_CMD="
if /I "%~1"=="--no-pause" (
  set "NO_PAUSE=1"
)

call :resolve_python_cmd
if errorlevel 1 exit /b 1

if exist ".\skport_signin.exe" (
  set "SKPORT_SIGNIN_CMD=.\skport_signin.exe"
) else (
  call :has_working_venv
  if errorlevel 1 (
    if exist ".venv" (
      echo Existing virtual environment is invalid. Recreating .venv...
      rmdir /s /q ".venv"
      if exist ".venv" exit /b 1
    )
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 exit /b 1
  )

  "%VENV_PY%" -m pip install --upgrade pip
  if errorlevel 1 exit /b 1
  "%VENV_PY%" -m pip install -e .
  if errorlevel 1 exit /b 1

  set "SKPORT_SIGNIN_CMD=%VENV_PY% -m skport_signin"
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
goto :eof

:resolve_python_cmd
set "LOCAL_APPDATA_DIR=%LocalAppData%"
if not exist "%LOCAL_APPDATA_DIR%\Programs" (
  set "LOCAL_APPDATA_DIR=%USERPROFILE%\AppData\Local"
)

where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
  exit /b 0
)
where python >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=python"
  exit /b 0
)
if exist "%LOCAL_APPDATA_DIR%\Programs\Python\Launcher\py.exe" (
  set "PYTHON_CMD=\"%LOCAL_APPDATA_DIR%\Programs\Python\Launcher\py.exe\" -3"
  exit /b 0
)
for %%P in (
  "%LOCAL_APPDATA_DIR%\Programs\Python\Python313\python.exe"
  "%LOCAL_APPDATA_DIR%\Programs\Python\Python312\python.exe"
  "%LOCAL_APPDATA_DIR%\Programs\Python\Python311\python.exe"
) do (
  if exist "%%~P" (
    set "PYTHON_CMD=\"%%~P\""
    exit /b 0
  )
)
echo Python 3.11+ was not found. Install Python or add py/python to PATH.
if not defined NO_PAUSE pause
exit /b 1

:has_working_venv
if not exist "%VENV_PY%" exit /b 1
"%VENV_PY%" -c "import sys" >nul 2>nul
exit /b %ERRORLEVEL%
