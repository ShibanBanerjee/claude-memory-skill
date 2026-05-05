# Windows Setup Guide

## Installing Python

Download from [python.org](https://python.org). During installation, check **"Add Python to PATH"**.

## Step 1: Install the Python helper

Open PowerShell and run:

```powershell
Copy-Item scripts\mem.py "$env:USERPROFILE\mem.py"
```

Verify it copied:
```powershell
Test-Path "$env:USERPROFILE\mem.py"
```

## Step 2: Install the skill

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills\claude-memory" -Force
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\claude-memory\SKILL.md"
```

For Claude.ai: Settings → Skills → Upload Custom Skill → upload `SKILL.md`

## Step 3: Verify

```powershell
python "$env:USERPROFILE\mem.py" setup
```

Expected output:
```
✅ Claude Memory — local database ready
   Location: C:\Users\YourName\.claude_memory.db
   Memories stored: 0
```

## Notes

- The database lives at `C:\Users\YourName\.claude_memory.db`
- No configuration files, credentials, or external accounts are required
- Python's built-in `sqlite3` module handles all storage — no additional installs needed
- Use `python` rather than `python3` in PowerShell if `python3` is not recognised
