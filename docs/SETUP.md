# Setup Guide

## Prerequisites

- A [Supabase](https://supabase.com) account (free tier works)
- Claude Pro, Max, Team, or Enterprise
- Python 3.8+ and `pip install requests` (only for the REST fallback)

---

## Step 1: Create the Database Table

In your Supabase project, go to **SQL Editor → New Query**. Paste `schema.sql` and run it.

This creates:
- `claude_memories` table with UUID primary key, TIMESTAMPTZ, JSONB columns, and TEXT[] tags
- GIN indexes for full-text search and tag lookups
- A `BEFORE INSERT OR UPDATE` trigger that populates the `search_vector` column automatically

It's safe to run more than once — all statements use `IF NOT EXISTS` or `CREATE OR REPLACE`.

---

## Step 2: Choose a Connection Method

### Option A — Supabase MCP (recommended)

Configure the Supabase MCP integration in Claude's settings. Claude can then run SQL directly against your database — no files, no credentials to manage, works on every platform including Windows Claude Desktop.

Once MCP is configured, skip to Step 3.

### Option B — mem.py REST Fallback

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

Verify the connection:
```bash
python3 ~/mem.py setup
```

Expected:
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

Create `%USERPROFILE%\.claude_memory_config.json` with the same JSON. Then:
```powershell
python "$env:USERPROFILE\mem.py" setup
```

Your Supabase URL and anon key are at **Project Settings → API**.

---

## Step 3: Install the Skill

**Claude Desktop / Claude.ai:**
Settings → Skills → Add Custom Skill → select `SKILL.md`

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

---

## Step 4: Verify

In any Claude conversation, type:
```
/mem list
```

Expected:
```
No memories saved yet. Use /mem to save your first conversation.
```
(or a list of entries if you already have some)

---

## Using Setup Scripts

If you've cloned the repo:

```bash
# Mac / Linux
chmod +x scripts/setup.sh && ./scripts/setup.sh

# Windows PowerShell
.\scripts\setup.ps1
```

Or run the full environment checker:
```bash
python3 scripts/verify.py
```
