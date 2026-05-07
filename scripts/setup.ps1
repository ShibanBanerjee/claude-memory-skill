# claude-memory-skill — Setup Script (Windows PowerShell)
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     claude-memory-skill  Setup         ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# 1. Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Install from https://python.org (check 'Add Python to PATH')" -ForegroundColor Red
    exit 1
}

# 2. Check / install requests
Write-Host "[2/4] Checking requests library..." -ForegroundColor Yellow
$requestsCheck = python -c "import requests; print('ok')" 2>&1
if ($requestsCheck -eq "ok") {
    Write-Host "✓ requests already installed" -ForegroundColor Green
} else {
    Write-Host "Installing requests..."
    pip install requests
    Write-Host "✓ requests installed" -ForegroundColor Green
}

# 3. Install mem.py
Write-Host "[3/4] Installing mem.py..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$memSrc = Join-Path $scriptDir "mem.py"
if (-not (Test-Path $memSrc)) {
    $memSrc = Join-Path (Split-Path -Parent $scriptDir) "mem.py"
}
Copy-Item -Path $memSrc -Destination "$env:USERPROFILE\mem.py" -Force
Write-Host "✓ mem.py installed to $env:USERPROFILE\mem.py" -ForegroundColor Green

# 4. Check credentials and test connection
Write-Host "[4/4] Checking Supabase credentials..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.claude_memory_config.json"
if (-not (Test-Path $configPath)) {
    Write-Host ""
    Write-Host "  $configPath not found."
    Write-Host "  Create it with your Supabase project credentials:"
    Write-Host ""
    Write-Host '  {"supabase_url": "https://your-project.supabase.co", "supabase_anon_key": "your-anon-key"}'
    Write-Host ""
    Write-Host "  Your URL and anon key are at: Supabase Dashboard -> Project Settings -> API"
    Write-Host ""
    Write-Host "  Skipping connection test — create the config file and run: python `"$env:USERPROFILE\mem.py`" setup" -ForegroundColor Yellow
} else {
    python "$env:USERPROFILE\mem.py" setup
    Write-Host "✓ Supabase connection verified" -ForegroundColor Green
}

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""
Write-Host "Next step: install the skill in Claude"
Write-Host ""
Write-Host "  Claude Desktop: Settings -> Skills -> Add Custom Skill -> upload SKILL.md"
Write-Host ""
Write-Host "Then in any Claude conversation, type:"
Write-Host "  /mem      -> save conversation to memory"
Write-Host "  /context  -> restore memory in future sessions"
Write-Host ""
