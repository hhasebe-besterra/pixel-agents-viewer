# Pixel Agents Viewer - Stop script (browser mode)
# Kills the local HTTP server. Browser tab + VS Code are left alone.

$ErrorActionPreference = "SilentlyContinue"

$httpPidFile = Join-Path $PSScriptRoot ".http_pid"
if (Test-Path $httpPidFile) {
    $pidValue = Get-Content $httpPidFile
    if ($pidValue) {
        $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $pidValue -Force
            Write-Host "HTTP server stopped (PID $pidValue)." -ForegroundColor Green
        } else {
            Write-Host "HTTP server was not running." -ForegroundColor Gray
        }
    }
    Remove-Item $httpPidFile -Force
} else {
    Write-Host "HTTP server was not running." -ForegroundColor Gray
}
