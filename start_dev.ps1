# CampusPulse AI - Development Server Launcher
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CampusPulse AI - Development Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Setting DJANGO_RUNSERVER_HIDE_WARNING=true..." -ForegroundColor Yellow
$env:DJANGO_RUNSERVER_HIDE_WARNING = "true"

Write-Host "Starting Django Development Server at http://127.0.0.1:8000/ ..." -ForegroundColor Cyan
Write-Host "(Press CTRL+C to stop)" -ForegroundColor Gray
Write-Host ""

python manage.py runserver
