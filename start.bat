@echo off
rem Double-click this file to start the YouTube to MP3 app on Windows.
cd /d "%~dp0"

where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH",
    echo then double-click start.bat again.
    pause
    exit /b 1
)

if not exist .venv\Scripts\python.exe (
    echo Setting up for the first time. This takes a minute...
    %PY% -m venv .venv || goto :failed
)
.venv\Scripts\python.exe -m pip install -q --upgrade -r requirements.txt || goto :failed

.venv\Scripts\python.exe app.py
pause
exit /b 0

:failed
echo.
echo Setup failed. Check your internet connection and try again.
pause
exit /b 1
