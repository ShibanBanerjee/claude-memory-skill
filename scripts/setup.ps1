# claude-memory-skill — Setup Script (Windows PowerShell)
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     claude-memory-skill  Setup         ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# 1. Check Python
Write-Host "[1/3] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Install from https://python.org (check 'Add Python to PATH')" -ForegroundColor Red
    exit 1
}

# 2. Install mem.py
Write-Host "[2/3] Installing mem.py..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$memSrc = Join-Path $scriptDir "mem.py"
if (-not (Test-Path $memSrc)) {
    $memSrc = Join-Path (Split-Path -Parent $scriptDir) "mem.py"
}
Copy-Item -Path $memSrc -Destination "$env:USERPROFILE\mem.py" -Force
python "$env:USERPROFILE\mem.py" setup
Write-Host "✓ mem.py installed and database initialised" -ForegroundColor Green

# 3. Install SKILL.md
Write-Host "[3/3] Installing Claude skill..." -ForegroundColor Yellow
$skillDir = "$env:USERPROFILE\.claude\skills\claude-memory"
New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
$skillSrc = Join-Path (Split-Path -Parent $scriptDir) "SKILL.md"
if (-not (Test-Path $skillSrc)) { $skillSrc = "SKILL.md" }
Copy-Item -Path $skillSrc -Destination "$skillDir\SKILL.md" -Force
Write-Host "✓ SKILL.md installed to $skillDir" -ForegroundColor Green

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""
Write-Host "Setup complete. In any Claude conversation, type:"
Write-Host ""
Write-Host "  /mem      → save conversation to memory"
Write-Host "  /context  → restore memory in future sessions"
Write-Host ""
Write-Host "No further configuration required." -ForegroundColor Green
Write-Host ""
