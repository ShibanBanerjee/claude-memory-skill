# Windows Setup Guide

## Why Windows Needs a Different Approach

Claude Desktop on Windows runs its `bash_tool` inside an isolated **Linux container**. This container cannot access your Windows filesystem — so `~/mem.py` inside the container is not the same as `C:\Users\you\mem.py` on your real machine. Any files Claude installs inside its container disappear when the conversation ends.

The solution is `mem_server.py`: a lightweight Python HTTP server that runs on your real Windows machine and exposes the SQLite database over `localhost:7823`. Claude's container can reach your machine's localhost via `host.docker.internal`, so the bridge works cleanly.

**You do not need to understand any of this to use it.** Just follow the steps below.

---

## Full Install — Windows

### Step 1: Download mem_server.py

Open **PowerShell** (not Claude, not Command Prompt — your own PowerShell) and run:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"
```

This saves `mem_server.py` to `C:\Users\YourName\mem_server.py`.

---

### Step 2: Start the server

```powershell
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden
```

This starts the server as a hidden background process. You will not see a window.

---

### Step 3: Verify the server is running

```powershell
Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content
```

Expected output:
```json
{
  "status": "ok",
  "db": "C:\\Users\\YourName\\.claude_memory.db",
  "memories": 0,
  "version": "2.1.0"
}
```

If you see this, the server is running and the database is ready.

---

### Step 4: Install the skill in Claude Desktop

1. Open Claude Desktop
2. Settings → Skills → Add Custom Skill
3. Upload `SKILL.md` from this repo

---

### Step 5: Test it

Open a Claude Desktop conversation and type:
```
/mem list
```

Claude should respond with a memory list (empty on first use). If it does — you're fully set up.

---

## Auto-Start on Login (Recommended)

By default, the server stops when you reboot. To make it start automatically:

```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "$env:USERPROFILE\mem_server.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "ClaudeMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest
```

To verify the task was created:
```powershell
Get-ScheduledTask -TaskName "ClaudeMemoryServer"
```

To remove it later:
```powershell
Unregister-ScheduledTask -TaskName "ClaudeMemoryServer" -Confirm:$false
```

---

## Using the Startup Script

If you've cloned this repo, you can use the included script which handles everything above:

```powershell
.\scripts\start_mem_server.ps1
```

---

## Server Management

**Check if running:**
```powershell
Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content
```

**Stop the server:**
```powershell
Get-Process -Name "python*" | Where-Object { $_.CommandLine -like "*mem_server*" } | Stop-Process
```

**Restart:**
```powershell
# Stop first
Get-Process -Name "python*" | Where-Object { $_.CommandLine -like "*mem_server*" } | Stop-Process -ErrorAction SilentlyContinue
# Start again
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden
```

**View server log (if running from terminal):**
```powershell
python "$env:USERPROFILE\mem_server.py"
```

---

## Where Your Data Lives

```
C:\Users\YourName\.claude_memory.db
```

This is a standard SQLite file. You can back it up, copy it to another machine, or open it with any SQLite viewer.

**Back up your memories:**
```powershell
Copy-Item "$env:USERPROFILE\.claude_memory.db" "$env:USERPROFILE\claude_memory_backup.db"
```

---

## Troubleshooting

**`python: command not found` or `python is not recognized`**
Python is not installed or not on your PATH. Download from [python.org](https://python.org). During install, check "Add Python to PATH".

**`Connection refused` — Claude says mem_server.py is not running**
The server stopped (likely after a reboot). Run:
```powershell
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden
```
Set up Task Scheduler (Step above) to prevent this.

**`No such file` — PowerShell can't find mem_server.py**
The download in Step 1 didn't complete. Re-run the `Invoke-WebRequest` command.

**`python "$env:USERPROFILE\mem.py" setup` says `can't open file`**
You're running from `C:\WINDOWS\system32`. Always use the full path: `python "$env:USERPROFILE\mem.py"` not just `python mem.py`.

**Port 7823 is in use by another application**
Run the server on a different port:
```powershell
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py --port 7824" -WindowStyle Hidden
```
Note: if you change the port you must also update the port number in SKILL.md (Step 0 detection block).

---

## Technical Notes (for the curious)

Claude Desktop's bash_tool on Windows runs inside a Docker-based Linux container. Containers cannot access the host Windows filesystem. They can, however, reach the host machine via `host.docker.internal` (Docker's built-in hostname for the Windows host). `mem_server.py` listens on `0.0.0.0:7823` (all interfaces), which makes it reachable from the container. SKILL.md's Step 0 probes `localhost`, `host.docker.internal`, and common Docker bridge IPs in sequence to find whichever route works.
