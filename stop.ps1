# Pixel Agents Viewer - Stop script

$ErrorActionPreference = "SilentlyContinue"

$obs = Get-Process "obs64" -ErrorAction SilentlyContinue
if ($obs) {
    Stop-Process -Name "obs64" -Force
    Write-Host "OBS stopped." -ForegroundColor Green
} else {
    Write-Host "OBS was not running." -ForegroundColor Gray
}
