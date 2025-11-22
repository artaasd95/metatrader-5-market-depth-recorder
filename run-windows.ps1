# PowerShell script to run the MT5 Market Depth Loader on Windows
# This script should be run directly on the Windows host, not in Docker

Write-Host "Starting MT5 Market Depth Loader on Windows Host..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check if requirements are installed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting MT5 Market Depth Loader" -ForegroundColor Green
Write-Host "InfluxDB URL: $env:INFLUX_URL" -ForegroundColor Cyan
Write-Host "Symbol: $env:SYMBOL" -ForegroundColor Cyan
Write-Host "Timezone: $env:TIMEZONE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the loader" -ForegroundColor Yellow
Write-Host ""

# Run the loader
python src/orderbook_loader.py