# Pixel Agents Viewer - Setup script
# Run once to prepare environment

$ErrorActionPreference = "Stop"

Write-Host "=== Pixel Agents Viewer Setup ===" -ForegroundColor Cyan

# 1. Install OBS Studio if missing
$obsPath = "C:\Program Files\obs-studio\bin\64bit\obs64.exe"
if (-not (Test-Path $obsPath)) {
    Write-Host "[1/3] Installing OBS Studio via winget..." -ForegroundColor Yellow
    winget install --id OBSProject.OBSStudio -e --silent --accept-source-agreements --accept-package-agreements
} else {
    Write-Host "[1/3] OBS Studio already installed." -ForegroundColor Green
}

# 2. Enable OBS WebSocket
Write-Host "[2/3] Configuring OBS WebSocket..." -ForegroundColor Yellow
$wsConfigDir = "$env:APPDATA\obs-studio\plugin_config\obs-websocket"
New-Item -ItemType Directory -Path $wsConfigDir -Force | Out-Null

$wsConfig = @{
    alerts_enabled  = $false
    auth_required   = $true
    first_load      = $false
    server_enabled  = $true
    server_password = "pixelagents"
    server_port     = 4455
} | ConvertTo-Json

Set-Content -Path "$wsConfigDir\config.json" -Value $wsConfig -Encoding UTF8
Write-Host "    WebSocket enabled on port 4455 (password: pixelagents)" -ForegroundColor Green

# 3. Install Python dependency
Write-Host "[3/3] Installing obsws-python..." -ForegroundColor Yellow
python -m pip install --quiet --upgrade obsws-python

Write-Host ""
Write-Host "Setup complete. Run .\launch.ps1 to start." -ForegroundColor Cyan
