# PowerShell setup script for Windows environment
# This script helps set up the Python environment for running the MT5 loader

Write-Host "Setting up MT5 Market Depth Loader on Windows..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.12+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "Please configure your .env file with InfluxDB and MT5 settings" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Start InfluxDB with: docker compose up influxdb -d" -ForegroundColor White
Write-Host "3. Run the loader with: .\run-windows.ps1" -ForegroundColor White
Write-Host ""

# Offer to start InfluxDB
$startInflux = Read-Host "Do you want to start InfluxDB now? (y/N)"
if ($startInflux -eq 'y' -or $startInflux -eq 'Y') {
    Write-Host "Starting InfluxDB..." -ForegroundColor Yellow
    docker compose up influxdb -d
    Write-Host "✓ InfluxDB started" -ForegroundColor Green
    Write-Host "You can access it at: http://localhost:8086" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "To run the MT5 loader, execute: .\run-windows.ps1" -ForegroundColor Green