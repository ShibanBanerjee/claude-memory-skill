# Setup Guide

## Prerequisites

- Python 3.8+ — no additional packages required
- Claude.ai Pro/Max/Team/Enterprise, or Claude Code

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

**For Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

**For Claude.ai:**
Settings → Skills → Upload Custom Skill → upload `SKILL.md`

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

The database at `~/.claude_memory.db` is created automatically on first use. There is nothing else to configure.

## Step 4: Test end to end

In a Claude conversation, type:
```
/mem Test Memory
```

Claude generates a summary of the conversation and stores it. You'll receive a memory ID and a restore command. In a new conversation:
```
/context test
```

Claude retrieves and loads the saved memory.

## Optional: Run the full verifier

```bash
python3 scripts/verify.py
```

This checks Python version, SQLite FTS5 availability, `mem.py` installation, database connectivity, and skill placement.
