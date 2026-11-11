@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0runtime\python.exe" (
    "%~dp0runtime\python.exe" "%~dp0fusionlocks.py" %*
    exit /b %errorlevel%
)

where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0fusionlocks.py" %*
    exit /b %errorlevel%
)

where python >nul 2>nul
if not errorlevel 1 (
    python "%~dp0fusionlocks.py" %*
    exit /b %errorlevel%
)

echo Python 3 was not found. See README.en.md or README.it.md for portable setup.
exit /b 1
