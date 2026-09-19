# CampusPulse AI - Windows PowerShell Production Launcher
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CampusPulse AI" -ForegroundColor Green
Write-Host "Production WSGI Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server:" -ForegroundColor Yellow
Write-Host "http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""
Write-Host "Starting Waitress..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "$env:APPDATA\Python\Python314\Scripts") {
    $env:PATH += ";$env:APPDATA\Python\Python314\Scripts"
}

# Verify waitress module is available
try {
    python -c "import waitress" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Waitress is not installed. Run: pip install -r requirements.txt"
        exit 1
    }
} catch {
    Write-Error "Python is not accessible."
    exit 1
}

if (Get-Command waitress-serve -ErrorAction SilentlyContinue) {
    waitress-serve --listen=127.0.0.1:8000 config.wsgi:application
} else {
    python -m waitress --listen=127.0.0.1:8000 config.wsgi:application
}
