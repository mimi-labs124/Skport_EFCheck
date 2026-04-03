@echo off
setlocal
cd /d "%~dp0"
set "VENV_PY=.venv\Scripts\python.exe"

if exist ".\skport_signin.exe" (
  ".\skport_signin.exe" run %*
) else (
  call :has_working_venv
  if not errorlevel 1 (
    "%VENV_PY%" -m skport_signin run %*
  ) else (
    where py >nul 2>nul
    if errorlevel 1 (
      python -m skport_signin run %*
    ) else (
      py -3 -m skport_signin run %*
    )
  )
)
endlocal
goto :eof

:has_working_venv
if not exist "%VENV_PY%" exit /b 1
"%VENV_PY%" -c "import sys" >nul 2>nul
exit /b %ERRORLEVEL%
