# Pixel Agents Viewer - Stop script
# Captures current Projector geometry, then shuts OBS down.

$ErrorActionPreference = "SilentlyContinue"

$obs = Get-Process "obs64" -ErrorAction SilentlyContinue
if ($obs) {
    python "$PSScriptRoot\save_geometry.py"
    Stop-Process -Name "obs64" -Force
    Write-Host "OBS stopped." -ForegroundColor Green
} else {
    Write-Host "OBS was not running." -ForegroundColor Gray
}
