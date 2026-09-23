@echo off
setlocal
set "SCRIPT=%~dp0lookup"
where py >nul 2>&1 && (
  py -3 "%SCRIPT%" %*
  exit /b %ERRORLEVEL%
)
where python >nul 2>&1 && (
  python "%SCRIPT%" %*
  exit /b %ERRORLEVEL%
)
where python3 >nul 2>&1 && (
  python3 "%SCRIPT%" %*
  exit /b %ERRORLEVEL%
)
echo Python 3 is required. Install from https://www.python.org/downloads/
echo During setup, check "Add python.exe to PATH".
exit /b 1
