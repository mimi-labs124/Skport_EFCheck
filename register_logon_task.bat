@echo off
setlocal
cd /d "%~dp0"
set "VENV_PY=.venv\Scripts\python.exe"

set "EXTRA_ARGS=register-task"
if /I "%~1"=="--no-pause" (
  set "EXTRA_ARGS=%EXTRA_ARGS% --no-pause"
)

if exist ".\skport_signin.exe" (
  ".\skport_signin.exe" %EXTRA_ARGS%
  set "EXIT_CODE=%ERRORLEVEL%"
) else (
  call :has_working_venv
  if not errorlevel 1 (
    "%VENV_PY%" -m skport_signin %EXTRA_ARGS%
    set "EXIT_CODE=%ERRORLEVEL%"
  ) else (
    where py >nul 2>nul
    if errorlevel 1 (
      python -m skport_signin %EXTRA_ARGS%
      set "EXIT_CODE=%ERRORLEVEL%"
    ) else (
      py -3 -m skport_signin %EXTRA_ARGS%
      set "EXIT_CODE=%ERRORLEVEL%"
    )
  )
)

if not "%~1"=="--no-pause" (
  pause
)

endlocal
exit /b %EXIT_CODE%
goto :eof

:has_working_venv
if not exist "%VENV_PY%" exit /b 1
"%VENV_PY%" -c "import sys" >nul 2>nul
exit /b %ERRORLEVEL%
