# Installation

## Prerequisites

- Python 3.8+
- A [Supabase](https://supabase.com) account (free tier works)
- Claude.ai Pro, Max, Team, or Enterprise — or Claude Code

For a quicker path, run the platform-specific setup script:

```bash
# Mac/Linux
chmod +x scripts/setup.sh && ./scripts/setup.sh

# Windows PowerShell
.\scripts\setup.ps1
```

Or follow the steps below manually.

---

## Step 1: Create the database table

In your Supabase dashboard, open **SQL Editor → New Query**, paste the contents of `scripts/schema.sql`, and run it.

## Step 2: Create the config file

**Mac/Linux:**
```bash
cat > ~/.claude_memory_config.json << 'CONF'
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "eyJhbGci..."
}
CONF
```

**Windows PowerShell:**
```powershell
@'
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "eyJhbGci..."
}
'@ | Out-File -FilePath "$env:USERPROFILE\.claude_memory_config.json" -Encoding utf8
```

Get your key from: **Supabase → Settings → API Keys → Legacy anon tab** (the JWT starting with `eyJ...`).

> The new publishable key format requires domain whitelisting and won't work for local scripts. Use the legacy anon key.

## Step 3: Install the Python helper

```bash
pip install requests --break-system-packages
cp scripts/mem.py ~/mem.py
python3 ~/mem.py setup
```

Expected output:
```
Claude Memory Skill v1.2.0
Connected to Supabase successfully.
Table: claude_memories — 0 memories stored.
```

## Step 4: Install the skill

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

**Claude.ai:** Settings → Skills → Upload Custom Skill → select `SKILL.md`

## Step 5: Verify everything

```bash
python3 scripts/verify.py
```

## Step 6: Test it

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
| `scripts/mem.py` | CLI helper for local use |
| `scripts/schema.sql` | Database schema — run once in Supabase |
| `scripts/verify.py` | Checks your installation end-to-end |
| `~/.claude_memory_config.json` | Supabase credentials (never commit this) |
