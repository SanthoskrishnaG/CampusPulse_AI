@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo CampusPulse AI
echo Production WSGI Server
echo ========================================
echo.
echo Server:
echo http://127.0.0.1:8000/
echo.
echo Starting Waitress...
echo.

REM Ensure user scripts directory is in PATH for waitress-serve
if exist "%APPDATA%\Python\Python314\Scripts" (
    set "PATH=%PATH%;%APPDATA%\Python\Python314\Scripts"
)

REM Verify Python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found on PATH.
    pause
    exit /b 1
)

REM Verify Waitress is installed
python -c "import waitress" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Waitress is not installed.
    echo Please install dependencies first: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if waitress-serve command is available directly
where waitress-serve >nul 2>nul
if %ERRORLEVEL% equ 0 (
    waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
) else (
    python -m waitress --listen=127.0.0.1:8000 config.wsgi:application
)

endlocal
