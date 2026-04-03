@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"
call ".\setup_windows.bat" --no-pause
if errorlevel 1 (
  echo Setup failed.
  pause
  exit /b 1
)

set "SKPORT_SIGNIN_CMD="
if exist ".\skport_signin.exe" (
  set "SKPORT_SIGNIN_CMD=.\skport_signin.exe"
) else (
  call :has_working_venv
  if not errorlevel 1 (
    set "SKPORT_SIGNIN_CMD=%VENV_PY% -m skport_signin"
  ) else (
    where py >nul 2>nul
    if errorlevel 1 (
      set "SKPORT_SIGNIN_CMD=python -m skport_signin"
    ) else (
      set "SKPORT_SIGNIN_CMD=py -3 -m skport_signin"
    )
  )
)

%SKPORT_SIGNIN_CMD% setup --interactive
if errorlevel 1 (
  echo.
  echo Failed while running the guided setup flow.
  pause
  exit /b 1
)
pause
endlocal
goto :eof

:has_working_venv
if not exist "%VENV_PY%" exit /b 1
"%VENV_PY%" -c "import sys" >nul 2>nul
exit /b %ERRORLEVEL%
