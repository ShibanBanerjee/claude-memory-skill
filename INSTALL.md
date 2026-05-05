# Installation

## Prerequisites

- Python 3.8+ — standard library only, no pip installs required
- Claude.ai Pro, Max, Team, or Enterprise — or Claude Code

Run the platform-specific setup script for the fastest path:

```bash
# Mac / Linux
chmod +x scripts/setup.sh && ./scripts/setup.sh

# Windows PowerShell
.\scripts\setup.ps1
```

Or follow the steps below manually.

---

## Step 1: Install the Python helper

**Mac / Linux:**
```bash
cp scripts/mem.py ~/mem.py
chmod +x ~/mem.py
```

**Windows PowerShell:**
```powershell
Copy-Item scripts\mem.py "$env:USERPROFILE\mem.py"
```

## Step 2: Install the skill

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

**Claude.ai:** Settings → Skills → Upload Custom Skill → select `SKILL.md`

## Step 3: Verify

```bash
python3 ~/mem.py setup
```

Expected output:
```
✅ Claude Memory — local database ready
   Location: /home/you/.claude_memory.db
   Memories stored: 0
```

The database is created automatically. No further setup is required.

## Step 4: Test it

In any Claude conversation:
```
/mem My first memory
```

Claude generates a summary of the conversation, stores it, and returns a memory ID. In any future session:
```
/context my first memory
```

---

## File reference

| File | Purpose |
|---|---|
| `SKILL.md` | Skill definition — tells Claude how to handle `/mem` and `/context` |
| `scripts/mem.py` | Copy to `~/mem.py` — handles all local database operations |
| `scripts/verify.py` | Checks your installation end-to-end |
| `~/.claude_memory.db` | Your memory database — created automatically on first use |
