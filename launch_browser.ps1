# Pixel Agents Viewer - Browser mode launcher
# Starts VS Code, serves viewer.html locally, opens the browser.
# Uses the browser's getDisplayMedia API — no OBS / no virtual camera needed.

$ErrorActionPreference = "Stop"

# Ensure VS Code is running (Pixel Agents panel must be visible as capture source)
$vscode = Get-Process "Code" -ErrorAction SilentlyContinue
if (-not $vscode) {
    $vscodeCandidates = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "C:\Program Files\Microsoft VS Code\Code.exe",
        "C:\Program Files (x86)\Microsoft VS Code\Code.exe"
    )
    $vscodePath = $vscodeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($vscodePath) {
        Write-Host "Starting VS Code..." -ForegroundColor Yellow
        Start-Process $vscodePath
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Seconds 1
            $p = Get-Process "Code" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle }
            if ($p) { break }
        }
    } else {
        Write-Host "Warning: VS Code not found. Start it manually." -ForegroundColor Red
    }
} else {
    Write-Host "VS Code already running." -ForegroundColor Green
}

# Start local HTTP server — getDisplayMedia requires a secure context (localhost qualifies)
$httpPidFile = Join-Path $PSScriptRoot ".http_pid"
$existingPid = $null
if (Test-Path $httpPidFile) { $existingPid = Get-Content $httpPidFile -ErrorAction SilentlyContinue }
$existingProc = $null
if ($existingPid) { $existingProc = Get-Process -Id $existingPid -ErrorAction SilentlyContinue }

if (-not $existingProc) {
    Write-Host "Starting local HTTP server on 127.0.0.1:8765..." -ForegroundColor Yellow
    $http = Start-Process python `
        -ArgumentList "-m", "http.server", "8765", "--bind", "127.0.0.1", "--directory", $PSScriptRoot `
        -WindowStyle Hidden -PassThru
    $http.Id | Set-Content $httpPidFile
    Start-Sleep -Milliseconds 500
} else {
    Write-Host "HTTP server already running (PID $($existingProc.Id))." -ForegroundColor Green
}

# Open browser
$url = "http://127.0.0.1:8765/viewer.html"
Start-Process $url
Write-Host ""
Write-Host "Browser viewer opened: $url" -ForegroundColor Cyan
Write-Host "Click the button on the page and pick the VS Code window." -ForegroundColor Cyan
Write-Host "Stop with: .\stop.ps1" -ForegroundColor Gray
