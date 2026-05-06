# Troubleshooting

## Installation Issues

### `mem.py isn't installed yet` (Mac/Linux)
Claude cannot find `~/mem.py`. Run this in your own terminal:
```bash
curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py
python3 ~/mem.py setup
```

### `mem_server.py` / `Connection refused` (Windows)
The HTTP server is not running. Open PowerShell and run:
```powershell
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden
```
Then verify: `Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content`

If `mem_server.py` doesn't exist yet:
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"
```

### `python3: command not found`
Install Python 3.8+ from [python.org](https://python.org). On Windows, use `python` instead of `python3` and check "Add Python to PATH" during installation.

### `can't open file 'C:\WINDOWS\system32\mem.py'`
You ran `python mem.py` from the system32 directory. Always use the full path:
```powershell
python "$env:USERPROFILE\mem.py" setup
```

### Skills not appearing in Claude
- Confirm you have a Pro, Max, Team, or Enterprise plan — free tier has no Skills access.
- Re-upload `SKILL.md` via Settings → Skills → Remove existing → Add Custom Skill.
- In Claude Desktop, fully quit and relaunch after uploading a new skill.

---

## Runtime Issues

### `/mem list` shows empty even though I've saved memories

**Mac/Linux:** Check that `~/.claude_memory.db` exists and has size > 0:
```bash
ls -lh ~/.claude_memory.db
```

**Windows:** Check that the server is pointing to the right database:
```powershell
Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content
```
The `db` field shows the exact path being used.

### `/context` finds nothing when I search

Try simpler, shorter search terms. Then use `/mem list` to browse all memories directly and confirm they were saved.

### `ERROR: Invalid JSON`
This is rare, usually caused by unescaped special characters in very long conversations. Claude will rebuild the JSON and retry automatically. If it persists, try saving a shorter segment of the conversation.

### Memory saved but Claude doesn't use it properly
Make sure you're using `/context [topic]` — not just mentioning the topic. Claude must explicitly load a memory before it becomes active context.

---

## Windows-Specific Issues

### Server stops after reboot
Add it to Task Scheduler:
```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "$env:USERPROFILE\mem_server.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "ClaudeMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest
```

### Port 7823 already in use
Run the server on a different port:
```powershell
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py --port 7824" -WindowStyle Hidden
```
Update the port in SKILL.md's Step 0 detection block to match.

### `host.docker.internal` doesn't resolve
This can happen on older Docker Desktop versions. Try updating Docker Desktop. If the issue persists, find your Docker bridge IP:
```powershell
docker network inspect bridge
```
And add that IP to the host probing list in SKILL.md Step 0.

### Claude on Windows says `MODE=none` — can't detect either direct or HTTP
1. Confirm `mem_server.py` is running: `Invoke-WebRequest http://localhost:7823/health`
2. If that works but Claude still says MODE=none, the container may not be reaching your host. Try running the server with verbose output: `python "$env:USERPROFILE\mem_server.py"` in a terminal window to see incoming requests.

---

## Data Issues

### I accidentally deleted a memory
Memories cannot be un-deleted through the skill. If you have a backup:
```bash
# Mac/Linux
cp ~/claude_memory_backup.db ~/.claude_memory.db

# Windows PowerShell
Copy-Item "$env:USERPROFILE\claude_memory_backup.db" "$env:USERPROFILE\.claude_memory.db"
```

### I want to start fresh
```bash
# Mac/Linux
rm ~/.claude_memory.db
python3 ~/mem.py setup

# Windows PowerShell
Remove-Item "$env:USERPROFILE\.claude_memory.db"
python "$env:USERPROFILE\mem_server.py"   # will recreate on start
```

### How do I view my database directly?
Use any SQLite viewer. [DB Browser for SQLite](https://sqlitebrowser.org/) is free and works on Mac, Linux, and Windows. Point it at `~/.claude_memory.db` (Mac/Linux) or `C:\Users\YourName\.claude_memory.db` (Windows).
