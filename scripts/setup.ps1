# claude-memory-skill — Setup Script (Windows PowerShell)
# Usage: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     claude-memory-skill  Setup         ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# 1. Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# 2. Install requests
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install requests -q
Write-Host "✓ requests library installed" -ForegroundColor Green

# 3. Copy mem.py
Write-Host "[3/5] Installing mem.py..." -ForegroundColor Yellow
Copy-Item -Path "mem.py" -Destination "$env:USERPROFILE\mem.py" -Force
Write-Host "✓ mem.py installed to $env:USERPROFILE\mem.py" -ForegroundColor Green

# 4. Create config if it doesn't exist
Write-Host "[4/5] Checking config file..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.claude_memory_config.json"
if (Test-Path $configPath) {
    Write-Host "✓ Config already exists at $configPath" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Config file not found. Let's create it."
    Write-Host "You'll need your Supabase project URL and anon key."
    Write-Host "Find them at: Supabase Dashboard → Project Settings → API Keys → Legacy anon key"
    Write-Host ""
    $supabaseUrl = Read-Host "Supabase project URL (e.g. https://abc123.supabase.co)"
    $supabaseKey = Read-Host "Supabase anon key (starts with eyJ...)"
    
    $config = @"
{
  "supabase_url": "$supabaseUrl",
  "supabase_anon_key": "$supabaseKey"
}
"@
    $config | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "✓ Config created at $configPath" -ForegroundColor Green
}

# 5. Install SKILL.md
Write-Host "[5/5] Installing Claude skill..." -ForegroundColor Yellow
Write-Host "⚠ Copy SKILL.md manually to your Claude skills directory." -ForegroundColor Yellow
Write-Host "  Typically: /mnt/skills/user/claude-memory/SKILL.md" -ForegroundColor Yellow

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Blue
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "  1. Run schema.sql in your Supabase SQL Editor"
Write-Host "     (Supabase Dashboard → SQL Editor → paste schema.sql → Run)"
Write-Host ""
Write-Host "  2. Test your connection:"
Write-Host "     python $env:USERPROFILE\mem.py setup"
Write-Host ""
Write-Host "  3. In any Claude conversation, type:"
Write-Host "     /mem      → save conversation to memory"
Write-Host "     /context  → restore memory in future sessions"
Write-Host ""
Write-Host "Setup complete. See docs/ for full documentation." -ForegroundColor Green
Write-Host ""
