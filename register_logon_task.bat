@echo off
setlocal
cd /d "%~dp0"

set "EXTRA_ARGS=register-task"
if /I "%~1"=="--no-pause" (
  set "EXTRA_ARGS=%EXTRA_ARGS% --no-pause"
)

if exist ".\efcheck.exe" (
  ".\efcheck.exe" %EXTRA_ARGS%
  set "EXIT_CODE=%ERRORLEVEL%"
) else if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m efcheck %EXTRA_ARGS%
  set "EXIT_CODE=%ERRORLEVEL%"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m efcheck %EXTRA_ARGS%
    set "EXIT_CODE=%ERRORLEVEL%"
  ) else (
    py -3 -m efcheck %EXTRA_ARGS%
    set "EXIT_CODE=%ERRORLEVEL%"
  )
)

if not "%~1"=="--no-pause" (
  pause
)

endlocal
exit /b %EXIT_CODE%
