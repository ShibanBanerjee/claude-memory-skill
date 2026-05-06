# start_mem_server.ps1
# Starts the Claude Memory Server in the background on Windows.
# Run this once. Add to Task Scheduler to start automatically on login.

$ServerScript = "$env:USERPROFILE\mem_server.py"

# Check if mem_server.py exists
if (-not (Test-Path $ServerScript)) {
    Write-Host "Downloading mem_server.py..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile $ServerScript
    Write-Host "Downloaded to $ServerScript" -ForegroundColor Green
}

# Check if already running
$existing = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*mem_server.py*"
}
if ($existing) {
    Write-Host "Claude Memory Server is already running (PID $($existing.Id))" -ForegroundColor Cyan
    exit 0
}

# Start in background, hidden window
$process = Start-Process python `
    -ArgumentList "`"$ServerScript`"" `
    -WindowStyle Hidden `
    -PassThru

Write-Host ""
Write-Host "✅ Claude Memory Server started" -ForegroundColor Green
Write-Host "   PID    : $($process.Id)" -ForegroundColor Gray
Write-Host "   Health : http://localhost:7823/health" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop: Stop-Process -Id $($process.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "To auto-start on login, run:" -ForegroundColor Yellow
Write-Host '  $action  = New-ScheduledTaskAction -Execute "python" -Argument "$env:USERPROFILE\mem_server.py"' -ForegroundColor Gray
Write-Host '  $trigger = New-ScheduledTaskTrigger -AtLogOn' -ForegroundColor Gray
Write-Host '  Register-ScheduledTask -TaskName "ClaudeMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest' -ForegroundColor Gray
