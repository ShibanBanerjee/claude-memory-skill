# Installation Guide

## Prerequisites

- Python 3.8+ — standard library only, zero pip installs
- Claude Pro, Max, Team, or Enterprise (Skills not available on free tier)

---

## Mac / Linux — Quick Install

```bash
# 1. Download mem.py to your home directory
curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py

# 2. Verify
python3 ~/mem.py setup
```

Expected output:
```
✅ Claude Memory — local database ready
   Location: /home/you/.claude_memory.db
   Memories stored: 0
```

Then install the skill in Claude:
- **Claude Desktop / Claude.ai:** Settings → Skills → Add Custom Skill → upload `SKILL.md`
- **Claude Code:** `mkdir -p ~/.claude/skills/claude-memory && cp SKILL.md ~/.claude/skills/claude-memory/`

---

## Windows — Quick Install

Claude Desktop on Windows runs bash commands inside a Linux container that cannot access your Windows filesystem. The solution is `mem_server.py` — a lightweight local HTTP server that runs on your real machine and Claude reaches it over localhost.

**Run these commands in PowerShell:**

```powershell
# 1. Download mem_server.py
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"

# 2. Start the server (hidden background process)
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden

# 3. Verify
Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content
```

Expected output:
```json
{"status": "ok", "db": "C:\\Users\\you\\.claude_memory.db", "memories": 0, "version": "2.1.0"}
```

**Auto-start on login (recommended):**
```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "$env:USERPROFILE\mem_server.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "ClaudeMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest
```

Then install the skill:
- Open Claude Desktop → Settings → Skills → Add Custom Skill → upload `SKILL.md`

For full Windows documentation see [docs/WINDOWS.md](docs/WINDOWS.md).

---

## Using Setup Scripts (if you've cloned the repo)

```bash
# Mac / Linux
chmod +x scripts/start_mem_server.sh && ./scripts/start_mem_server.sh

# Windows PowerShell
.\scripts\start_mem_server.ps1
```

---

## Verify Your Install

After installing, open a Claude conversation and type:

```
/mem list
```

If it returns `No memories saved yet` — you're fully installed. If it returns an error, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## File Reference

| File | Platform | Copy to |
|---|---|---|
| `SKILL.md` | All | Upload to Claude via Settings → Skills |
| `mem.py` | Mac / Linux | `~/mem.py` |
| `mem_server.py` | Windows | `%USERPROFILE%\mem_server.py` |
| `~/.claude_memory.db` | Mac / Linux | Created automatically |
| `C:\Users\you\.claude_memory.db` | Windows | Created automatically |
