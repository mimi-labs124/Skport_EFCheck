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

echo.
set /p ENABLE_ENDFIELD=Enable Endfield sign-in? [Y/n]:
set /p ENABLE_ARKNIGHTS=Enable Arknights sign-in? [y/N]:

set "ENABLE_ENDFIELD_NORMALIZED=%ENABLE_ENDFIELD%"
if not defined ENABLE_ENDFIELD_NORMALIZED set "ENABLE_ENDFIELD_NORMALIZED=Y"
set "ENABLE_ARKNIGHTS_NORMALIZED=%ENABLE_ARKNIGHTS%"
if not defined ENABLE_ARKNIGHTS_NORMALIZED set "ENABLE_ARKNIGHTS_NORMALIZED=N"

if /I not "%ENABLE_ENDFIELD_NORMALIZED%"=="Y" if /I not "%ENABLE_ARKNIGHTS_NORMALIZED%"=="Y" (
  echo No site selected. Defaulting to Endfield enabled.
  set "ENABLE_ENDFIELD_NORMALIZED=Y"
)

set "CONFIGURE_ARGS="
if /I "%ENABLE_ENDFIELD_NORMALIZED%"=="Y" (
  set "CONFIGURE_ARGS=!CONFIGURE_ARGS! --enable-site endfield"
) else (
  set "CONFIGURE_ARGS=!CONFIGURE_ARGS! --disable-site endfield"
)
if /I "%ENABLE_ARKNIGHTS_NORMALIZED%"=="Y" (
  set "CONFIGURE_ARGS=!CONFIGURE_ARGS! --enable-site arknights"
) else (
  set "CONFIGURE_ARGS=!CONFIGURE_ARGS! --disable-site arknights"
)

if /I "%ENABLE_ENDFIELD_NORMALIZED%"=="Y" if /I "%ENABLE_ARKNIGHTS_NORMALIZED%"=="Y" (
  echo.
  set /p SHARE_PROFILE=Share Endfield browser profile with Arknights? [Y/N]:
  if /I "%SHARE_PROFILE%"=="Y" (
    set "CONFIGURE_ARGS=!CONFIGURE_ARGS! --share-arknights-profile"
  )
)

%SKPORT_SIGNIN_CMD% configure-sites !CONFIGURE_ARGS!
if errorlevel 1 (
  echo.
  echo Failed while updating site configuration.
  pause
  exit /b 1
)

echo.
set /p CAPTURE_NOW=Capture your sign-in session now? [Y/N]:
if /I "%CAPTURE_NOW%"=="Y" (
  if /I "%ENABLE_ENDFIELD_NORMALIZED%"=="Y" (
    %SKPORT_SIGNIN_CMD% capture-session --site endfield
    if errorlevel 1 (
      echo.
      echo Failed while capturing the Endfield session.
      pause
      exit /b 1
    )
  )

  if /I "%ENABLE_ARKNIGHTS_NORMALIZED%"=="Y" (
    echo.
    echo Continue with the Arknights page in the same guided capture flow.
    %SKPORT_SIGNIN_CMD% capture-session --site arknights
    if errorlevel 1 (
      echo.
      echo Failed while capturing the Arknights session.
      pause
      exit /b 1
    )
  )
)

echo.
set /p REGISTER_TASK=Register the Windows logon scheduled task now? [Y/N]:
if /I "%REGISTER_TASK%"=="Y" (
  %SKPORT_SIGNIN_CMD% register-task --no-pause
  if errorlevel 1 (
    echo.
    echo Failed while registering the Windows logon task.
    pause
    exit /b 1
  )
)

echo.
echo Skport_Signin setup flow finished.
echo Manual tools remain available: capture_session.bat, run_signin.bat, register_logon_task.bat
pause
endlocal
goto :eof

:has_working_venv
if not exist "%VENV_PY%" exit /b 1
"%VENV_PY%" -c "import sys" >nul 2>nul
exit /b %ERRORLEVEL%
