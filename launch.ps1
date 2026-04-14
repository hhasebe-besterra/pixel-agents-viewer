# Pixel Agents Viewer - Launch script
# Starts OBS and opens an independent projector window for VS Code

$ErrorActionPreference = "Stop"

$obsPath = "C:\Program Files\obs-studio\bin\64bit\obs64.exe"
if (-not (Test-Path $obsPath)) {
    Write-Host "OBS Studio not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Ensure VS Code is running (so window capture has a target)
$vscode = Get-Process "Code" -ErrorAction SilentlyContinue
if (-not $vscode) {
    Write-Host "Warning: VS Code is not running. Start it and open Pixel Agents panel, then re-run." -ForegroundColor Yellow
}

# Start OBS if not already running
$obs = Get-Process "obs64" -ErrorAction SilentlyContinue
if (-not $obs) {
    Write-Host "Starting OBS..." -ForegroundColor Yellow
    Start-Process $obsPath `
        -ArgumentList "--minimize-to-tray", "--disable-shutdown-check" `
        -WorkingDirectory (Split-Path $obsPath -Parent)
} else {
    Write-Host "OBS already running." -ForegroundColor Green
}

# Wait for WebSocket to come up
Write-Host "Waiting for OBS WebSocket on port 4455..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 4455)
        $tcp.Close()
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "OBS WebSocket did not start within 30 seconds." -ForegroundColor Red
    exit 1
}

Write-Host "OBS ready. Opening projector..." -ForegroundColor Green

# Delegate scene/source/projector setup to Python
python "$PSScriptRoot\open_projector.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Projector window opened. Drag it to your preferred monitor." -ForegroundColor Cyan
    Write-Host "Stop with: .\stop.ps1" -ForegroundColor Gray
}
