# claude-memory-skill

Persistent, searchable memory for Claude — across every conversation, every device, every interface.

Type `/mem` to save what you're working on. Type `/context [topic]` in any future conversation to pick up exactly where you left off. Everything is stored in your own Supabase PostgreSQL database.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Claude Skills](https://img.shields.io/badge/Claude-Skill-blueviolet)](https://github.com/anthropics/skills) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org) [![Supabase](https://img.shields.io/badge/Storage-Supabase-green)](https://supabase.com) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## How it works

Two slash commands:

**`/mem`** — Claude reads the full conversation, extracts a structured memory (decisions, open questions, key entities, 1,500–4,000 word summary), and stores it in Supabase. If a memory for this project already exists, it updates rather than duplicates.

**`/context [topic]`** — Claude searches your stored memories by topic, loads the matching record into its working context, and resumes from the open questions without you having to re-explain anything.

The skill uses Supabase MCP as the primary storage path (no local setup needed) and falls back to a lightweight Python REST client if MCP is not configured.

---

## Prerequisites

- A [Supabase](https://supabase.com) account (free tier works fine)
- Claude Pro, Max, Team, or Enterprise

---

## Setup

### Step 1: Create the database table

Open your Supabase project → SQL Editor → New Query. Paste the contents of `schema.sql` and run it. This creates the `claude_memories` table with full-text search, JSONB fields, and the required indexes.

### Step 2: Connect Claude to Supabase

**Option A — Supabase MCP (recommended):**

Add the Supabase MCP integration to Claude's settings. Once connected, Claude can run SQL directly against your database — no local files, no credentials to manage. Works on every device including Windows.

**Option B — mem.py REST fallback:**

For environments without MCP, install the Python helper:

```bash
# Mac / Linux
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

```bash
python3 ~/mem.py setup
```

On Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py" -OutFile "$env:USERPROFILE\mem.py"
pip install requests
python "$env:USERPROFILE\mem.py" setup
```

Your Supabase URL and anon key are in: Project Settings → API.

### Step 3: Install the skill

**Claude Desktop / Claude.ai:** Settings → Skills → Add Custom Skill → upload `SKILL.md`

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

---

## Usage

### Saving a conversation

At any point in a conversation, type:
```
/mem
```

Claude saves it with an auto-generated title. For a specific title:
```
/mem Backend Architecture — Microservices Decision
/mem Devam Strategy Session May 2026
```

If a memory for this project already exists, it's updated rather than duplicated. Run `/mem` at any point in a long session to checkpoint, and again at the end — you'll always have one clean, comprehensive record.

### Restoring context

Open a new conversation and type:
```
/context backend architecture
/context devam strategy
/context auth service
```

Claude searches across title, project, summary, and tags simultaneously. It loads the matching memory and says "I have loaded the [project] context. [Orientation]. Where would you like to resume?" — no re-explaining needed.

### Listing all memories

```
/mem list
```

Returns all saved memories with title, project, date, tags, and word count.

---

## What gets stored

Each memory entry captures:

- **Summary** — 1,500 to 4,000 words. Every significant decision, the reasoning behind it, every idea considered and rejected, all specific numbers and names, current status, next steps, standing instructions.
- **Key decisions** — structured list, each entry including what was decided, why, and what was rejected
- **Open questions** — specific, actionable items that form the agenda for the next session
- **Entities** — people, products, companies, concepts, documents referenced in the conversation
- **Tags** — 5–10 searchable terms for future retrieval

The compression philosophy is lossless: a 3,000 word summary uses roughly 750 tokens when loaded into context — a trivial cost compared to the value of not losing a full session of work.

---

## Repository layout

```
SKILL.md                   Skill definition — upload this to Claude
schema.sql                 PostgreSQL schema — run once in Supabase SQL Editor
mem.py                     Python REST helper (fallback, requires pip install requests)
scripts/
  mem.py                   Same as root mem.py — for setup scripts
  schema.sql               Same as root schema.sql — for setup scripts
  setup.sh                 Mac/Linux automated setup
  setup.ps1                Windows PowerShell automated setup
  verify.py                Installation checker
  schema_pgvector.sql      Future: semantic search schema (not yet active)
docs/
  SETUP.md                 Detailed setup guide
  ADVANCED.md              Custom configuration and data management
  commands.md              Full command reference
  API_REFERENCE.md         mem.py CLI and PostgREST API reference
  TROUBLESHOOTING.md       Common issues and solutions
  architecture.md          How the skill works internally
references/
  MCP_REFERENCE.md         Supabase MCP SQL quick reference
  STORAGE_SPEC.md          Memory field specifications and quality standards
  RETRIEVAL_SPEC.md        Context restoration protocol
  QUALITY_RUBRIC.md        What makes a good memory entry
examples/
  example_memory.json      Sample stored memory record
  example_workflow.md      End-to-end save and restore walkthrough
  example_retrieval.md     Context retrieval example
tests/
  test_connection.py       Supabase connection test
  test_storage.py          Write/read/delete round-trip test
  test_search.py           Full-text search quality test
  run_all_tests.py         Run all tests
```

---

## Running the tests

```bash
# Requires ~/.claude_memory_config.json with valid Supabase credentials
python3 tests/run_all_tests.py
```

Or run individual checks:
```bash
python3 tests/test_connection.py
python3 scripts/verify.py
```

---

## Roadmap

- Semantic search using pgvector (find memories by meaning, not just keywords)
- Memory expiry and archival policies
- Multi-project context loading in a single `/context` call

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports, documentation improvements, and pull requests are welcome.
