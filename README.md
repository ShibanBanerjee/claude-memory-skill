# claude-memory-skill

Persistent, searchable memory for Claude — across every conversation, every device, every interface.

You're mid-way through a two-hour strategy session. Claude understands everything. Then the context window fills up, or you close the tab. Next conversation: blank slate.

**This skill fixes that.** Type `/mem` to save the conversation. Type `/context [topic]` in any new conversation to restore everything — decisions made, ideas rejected, open questions, all of it — without re-explaining a word.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org) [![Supabase](https://img.shields.io/badge/Storage-Supabase-3ECF8E?logo=supabase)](https://supabase.com) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## How it works

**Invoke the skill by typing `/mem` in any Claude conversation.**

The skill name is `mem`. It is triggered by:

| Command | What it does |
|---|---|
| `/mem` | Save the current conversation to memory |
| `/mem My Project Title` | Save with a specific title |
| `/mem list` | List all saved memories |
| `/context topic` | Restore a memory in a new conversation |
| `/recall topic` | Same as `/context` |

When you type `/mem`, Claude reads the entire conversation, extracts a structured summary (1,500–4,000 words), captures all decisions with their reasoning, flags open questions, and stores everything in your Supabase database. If a memory for this project already exists, it updates rather than duplicates — so you always have one clean, comprehensive record per project.

When you type `/context auth service` in a new conversation, Claude searches your memories, loads the match, and says: *"I've loaded the auth service context. You chose JWT over sessions for stateless scaling, and the open question is token refresh strategy. Where would you like to continue?"* — no re-explaining.

---

## What you need

- **A Supabase account** — free tier, no credit card needed → [supabase.com](https://supabase.com)
- **A Claude paid plan** — Pro, Max, Team, or Enterprise (Skills require a paid plan; free tier does not have Skills access)
- **Python 3.8+ and `pip`** — only if you're not using the Supabase MCP integration (see Step 2 below)

---

## Setup — 3 steps, ~10 minutes

### Step 1: Create your Supabase database

1. Go to [supabase.com](https://supabase.com) and sign in (or create a free account)
2. Click **New project**, give it a name (e.g. `claude-memory`), set a database password, choose a region close to you
3. Wait ~2 minutes for the project to provision
4. In the left sidebar, click **SQL Editor**
5. Click **New query**
6. Copy the entire contents of [`schema.sql`](schema.sql) from this repo and paste it into the editor
7. Click **Run** (or press `Ctrl+Enter` / `Cmd+Enter`)

You should see `Success. No rows returned.` — that's correct. The `claude_memories` table is now ready.

> **Where to find your URL and API key:** Left sidebar → **Project Settings** → **API**
> - `Project URL` → this is your `supabase_url`
> - Under **Project API keys**, use the `anon` `public` key → this is your `supabase_anon_key`

---

### Step 2: Connect Claude to Supabase

You have two options. **Pick the one that fits your setup:**

#### Option A — Supabase MCP (recommended for Claude Code and Claude Desktop)

The Supabase MCP lets Claude run SQL directly against your database — no local files or credentials to manage. This is the most reliable path and works on all platforms including Windows.

**For Claude Code**, add the Supabase MCP to your `~/.claude/claude_desktop_config.json` (or use `claude mcp add`):

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--read-write"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "your-supabase-access-token"
      }
    }
  }
}
```

Get your access token at: [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)

Once MCP is configured, skip to Step 3. The skill will automatically detect the MCP connection and use it.

#### Option B — mem.py REST helper (works everywhere, requires Python)

This option calls Supabase's REST API from your local machine. Use it if you're on Claude.ai without MCP, or prefer not to configure MCP.

**Mac / Linux:**
```bash
# Download the helper script
curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py

# Install the requests library
pip install requests
```

Create the credentials file at `~/.claude_memory_config.json`:
```json
{
  "supabase_url": "https://your-project-id.supabase.co",
  "supabase_anon_key": "your-anon-public-key"
}
```

Test it:
```bash
python3 ~/mem.py setup
```

Expected output:
```
Claude Memory — Supabase ready
   Project: https://your-project-id.supabase.co
   Memories stored: 0
```

**Windows (PowerShell):**
```powershell
# Download the helper script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py" -OutFile "$env:USERPROFILE\mem.py"

# Install the requests library
pip install requests
```

Create `%USERPROFILE%\.claude_memory_config.json` with the same JSON content as above.

Test it:
```powershell
python "$env:USERPROFILE\mem.py" setup
```

---

### Step 3: Install the skill in Claude

The skill is defined in `SKILL.md`. Install it in Claude:

**Claude.ai / Claude Desktop:**
1. Open Claude → click your profile icon → **Settings**
2. Go to **Skills** (or **Custom Skills**)
3. Click **Add Custom Skill** (or **Upload Skill**)
4. Select the `SKILL.md` file from this repo
5. Save

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

That's it. Restart Claude Desktop (if using it) and you're ready.

---

## Using the skill

### Save a conversation

At any point, type in Claude:

```
/mem
```

Or with a title:

```
/mem Backend Architecture — Decision Log
/mem Q2 Product Strategy
/mem Weekly 1:1 with Alex — May 2026
```

Claude will respond with something like:

```
✅ Memory saved. NEW entry

Title:     Backend Architecture — Decision Log
Project:   backend-architecture
Memory ID: a3f2c1d8-4e5b-4f6a-9c1d-2e3f4a5b6c7d
Summary:   ~1,840 words
Decisions: 6
Questions: 3
Tags:      architecture, microservices, postgres, api-design

Restore in any future session with: /context backend architecture
```

Run `/mem` again in a later conversation on the same project — it updates the existing memory instead of creating a duplicate.

### Restore context in a new conversation

Open a new Claude conversation and type:

```
/context backend architecture
```

Claude searches across title, project, summary, and tags simultaneously. It loads the full memory and orients you:

```
📚 Memory loaded: "Backend Architecture — Decision Log"
Saved: 2026-05-05 | Project: backend-architecture | ~1,840 words
6 decisions locked | 3 open questions

Context restored. You chose a modular monolith for the initial launch,
with explicit service boundaries for future extraction. The main open
question is database isolation strategy when services are eventually split.

Where would you like to continue?
```

No re-explaining. No context loss. Everything Claude knew in the previous session is immediately available.

### List all memories

```
/mem list
```

Returns a table of all stored memories with title, project, date, tags, and decision count.

### Aliases

All of these do the same thing as `/context`:
```
/recall backend architecture
/ctx backend
```

---

## What gets stored

Every memory entry captures:

| Field | Description |
|---|---|
| **Summary** | 1,500–4,000 word narrative. Every decision with its reasoning. Every rejected idea with its rejection reason. All specific numbers and names. Current status and next steps. |
| **Key decisions** | Structured list — what was decided, why, and what was rejected instead |
| **Open questions** | Specific, actionable questions — the agenda for the next session |
| **Instructions** | Any preferences or directives you gave Claude during the conversation |
| **Entities** | People, products, companies, concepts, and documents referenced |
| **Tags** | 5–10 searchable terms |

**The philosophy is lossless capture.** Most AI memory systems compress aggressively and lose the reasoning. This skill stores everything that matters — at 3,000 words per summary, that's roughly 750 tokens when loaded into context. A trivial cost compared to re-explaining two hours of work.

---

## Troubleshooting

**`/mem` does nothing / Claude doesn't recognise the command**
→ The skill is not installed. Go to Claude Settings → Skills and confirm `SKILL.md` is uploaded. In Claude Desktop, fully quit and relaunch after installing.

**`MODE=none` or "Memory storage is not configured"**
→ Neither MCP nor mem.py is working. Check that your MCP is configured (Option A) or that `~/mem.py` exists and `~/.claude_memory_config.json` has valid credentials (Option B). Run `python3 ~/mem.py setup` in your terminal to test.

**`ERROR: Config file not found`**
→ Create `~/.claude_memory_config.json` with your Supabase URL and anon key.

**`ERROR: requests library not found`**
→ Run `pip install requests`

**Supabase error 401 or 403**
→ Your anon key is wrong or the table doesn't exist. Confirm you ran `schema.sql` in the SQL Editor and that your anon key is the `public` key (not the `service_role` key).

**Supabase project is paused**
→ Free-tier projects pause after one week of inactivity. Go to your Supabase dashboard and click **Restore project**. Takes ~30 seconds.

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

---

## Roadmap

- Semantic search with pgvector — find memories by meaning, not just keywords
- Memory expiry and archival
- Multi-project context in a single `/context` call

---

## Contributing

Bug reports, docs improvements, and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT
