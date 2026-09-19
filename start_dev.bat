@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo CampusPulse AI - Development Server
echo ========================================
echo.
echo Setting DJANGO_RUNSERVER_HIDE_WARNING=true...
set DJANGO_RUNSERVER_HIDE_WARNING=true

echo Starting Django Development Server at http://127.0.0.1:8000/ ...
echo (Press CTRL+C or CTRL+BREAK to stop)
echo.

python manage.py runserver

endlocal
