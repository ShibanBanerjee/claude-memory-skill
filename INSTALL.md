# Installation Guide

## Prerequisites

- A [Supabase](https://supabase.com) account (free tier works fine — no credit card required)
- Claude Pro, Max, Team, or Enterprise (Skills require a paid plan)
- Python 3.8+ and `pip install requests` (only if using the REST fallback — not needed with MCP)

---

## Step 1: Create the Database Table

Open your Supabase project → **SQL Editor** → **New Query**. Paste the contents of `schema.sql` and click **Run**.

This creates the `claude_memories` table, full-text search trigger, and required indexes. It's idempotent — safe to run more than once.

Your Supabase URL and anon key are at: **Project Settings → API**.

---

## Step 2: Connect Claude to Supabase

Choose one option:

### Option A — Supabase MCP (recommended)

Configure the Supabase MCP integration in your Claude settings. Once connected, Claude runs SQL directly against your database — no local files, no credentials file, works on Windows without any additional setup.

With MCP configured, skip ahead to Step 3.

### Option B — mem.py REST Fallback

Use this if you don't have MCP configured. Requires Python and `requests`.

**Mac / Linux:**
```bash
curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py
pip install requests
```

Create `~/.claude_memory_config.json`:
```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_anon_key": "your-anon-key"
}
```

Verify:
```bash
python3 ~/mem.py setup
```

Expected output:
```
Claude Memory — Supabase ready
   Project: https://your-project.supabase.co
   Memories stored: 0
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py" -OutFile "$env:USERPROFILE\mem.py"
pip install requests
```

Create `%USERPROFILE%\.claude_memory_config.json`:
```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_anon_key": "your-anon-key"
}
```

Verify:
```powershell
python "$env:USERPROFILE\mem.py" setup
```

---

## Step 3: Install the Skill

**Claude Desktop / Claude.ai:**
Settings → Skills → Add Custom Skill → upload `SKILL.md`

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

---

## Step 4: Test End to End

In a Claude conversation, type:
```
/mem list
```

If it returns a count of stored memories (including 0 with a success message) — you're fully set up.

---

## Using the Setup Scripts (if you've cloned the repo)

```bash
# Mac / Linux
chmod +x scripts/setup.sh && ./scripts/setup.sh

# Windows PowerShell
.\scripts\setup.ps1
```

These scripts handle the mem.py download, credentials check, and skill installation in one pass.

---

## File Reference

| File | Purpose | Where |
|---|---|---|
| `SKILL.md` | Skill definition — upload to Claude | Settings → Skills |
| `schema.sql` | Database schema — run in Supabase SQL Editor | One-time |
| `mem.py` | Python REST helper | `~/mem.py` (Mac/Linux) or `%USERPROFILE%\mem.py` (Windows) |
| `~/.claude_memory_config.json` | Supabase credentials | Home directory |
