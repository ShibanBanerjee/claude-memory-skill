# Setup Guide

## Prerequisites
- Python 3.8+
- A Supabase account (free tier works)
- Claude.ai Pro/Max/Team/Enterprise, or Claude Code

## Step 1: Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose a name (e.g. "claude-mem") and region close to you
4. Note your project URL and API keys

## Step 2: Run the Schema
1. In your Supabase dashboard, go to **SQL Editor → New Query**
2. Copy the contents of `scripts/schema.sql`
3. Paste and click **Run**
4. You should see: "Success. No rows returned."

## Step 3: Get Your API Key
1. Go to **Settings → API Keys**
2. Click the **"Legacy anon, service_role API keys"** tab
3. Copy the `anon` key (the long JWT starting with `eyJ...`)

> **Why legacy?** The new publishable key format (`sb_publishable_...`) requires
> domain whitelisting and is designed for browser apps. For local scripts, the
> legacy anon key is the correct choice.

## Step 4: Create Config File

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

## Step 5: Install Python Helper

```bash
pip install requests --break-system-packages
cp scripts/mem.py ~/mem.py
python3 ~/mem.py setup
```

Expected output:
```
Claude Memory Skill v1.2.0
Config: /home/user/.claude_memory_config.json
URL: https://your-project.supabase.co
Testing connection...
Connected to Supabase successfully.
Table: claude_memories — 0 memories stored.
```

## Step 6: Install the Skill

**For Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

**For Claude.ai:**
Go to Settings → Skills → Upload Custom Skill → upload `SKILL.md`

## Step 7: Test End to End

In a Claude conversation, type:
```
/mem Test Memory
```

Claude should generate a summary, store it, and confirm with a memory ID.
Then in a new conversation:
```
/context test
```

Claude should retrieve and display the saved memory.
