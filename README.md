# 🧠 Claude Memory Skill

> **Persistent, searchable memory for Claude — stored locally on your machine. Works on Mac, Linux, and Windows.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Claude Skills](https://img.shields.io/badge/Claude-Skill-blueviolet)](https://github.com/anthropics/skills) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org) [![SQLite](https://img.shields.io/badge/Storage-SQLite-green)](https://sqlite.org) [![Version](https://img.shields.io/badge/version-2.1.0-blue)](CHANGELOG.md) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Type `/mem` to save. Type `/context` to restore.**

No accounts. No cloud. No configuration. Everything stays on your machine.

---

## ⚠️ Security Notice

This skill runs Python scripts on your local machine via `bash_tool`. Only install skills from sources you trust. `mem.py` and `mem_server.py` are pure Python standard library — zero external dependencies. All they do is read and write a local SQLite file.

---

## Prerequisites

| Requirement | Detail |
|---|---|
| **Claude plan** | Pro, Max, Team, or Enterprise. **Skills are not available on the free tier.** |
| **Platform** | Claude Desktop (macOS, Windows, Linux) · Claude.ai web · Claude Code |
| **Python** | 3.8 or higher — standard library only, no pip installs |

---

## The Problem This Solves

You spend three hours in a deep product brainstorm with Claude. Fifteen critical decisions. Four frameworks applied. A full strategy mapped with nuance that took hours to develop. Then you open a new conversation — and Claude knows nothing. Claude even starts forgetting earlier parts of the same long running conversation. It starts hallucinating in long running conversations, missing key details.

Claude Memory fixes this. One command saves everything. One command restores it in any future session, in any conversation. You can even load more than one memory in a new conversation, giving you the superpower to reference the details of multiple earlier conversations in a single session without overflooding your context window.

---

## ⚠️ How This Actually Works — Read This First

Claude Desktop uses `bash_tool` to run commands. On **Mac and Linux**, bash_tool runs directly on your real machine — so `mem.py` works via direct Python calls. On **Windows**, bash_tool runs inside an isolated Linux container that cannot touch your Windows filesystem — so a lightweight local HTTP server (`mem_server.py`) bridges the gap.

The SKILL.md auto-detects which mode to use. You do not need to configure anything.

**Critical:** Claude cannot install these files for you. You must run the install commands yourself in your own terminal. Anything Claude installs disappears when the conversation ends.

---

## How It Works

```
Your Conversation (hours of work)
         |
         |  /mem "My Project"
         v
Claude Memory Skill
  1. Auto-detects: direct python3 (Mac/Linux) or HTTP server (Windows)
  2. Reads the ENTIRE conversation from start to finish
  3. Generates detailed summary (1,500–4,000 words)
  4. Extracts: decisions + WHY, rejected ideas, open questions, entities, tags
  5. If memory exists for this project → UPDATES it
     If no memory exists → INSERTS new entry
     One clean memory per project. No duplicates.
         |
         v
~/.claude_memory.db  (SQLite — on your machine)
Your data. Your machine. Your control.
         |
         |  New conversation, any time later
         |  /context "project name"
         v
Claude, fully restored — decisions locked, agenda set, ready to continue
```

---

## Quick Start

### Mac / Linux

**Step 1 — Install mem.py:**
```bash
curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py
python3 ~/mem.py setup
```

Expected:
```
✅ Claude Memory — local database ready
   Location: /home/you/.claude_memory.db
   Memories stored: 0
```

**Step 2 — Install the skill in Claude:**
- **Claude Desktop / Claude.ai:** Settings → Skills → Add Custom Skill → upload `SKILL.md`
- **Claude Code:** `mkdir -p ~/.claude/skills/claude-memory && curl -o ~/.claude/skills/claude-memory/SKILL.md https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/SKILL.md`

**Step 3 — Use it:**
```
/mem "My Project"     # Save current conversation
/context my project   # Restore in any future session
/mem list             # Browse all saved memories
```

---

### Windows

Windows requires a local HTTP server because Claude Desktop's bash tool runs in an isolated Linux container that cannot access your Windows filesystem. `mem_server.py` runs on your real machine and Claude reaches it over localhost.

**Step 1 — Download and start the server (run this in PowerShell, once):**
```powershell
# Download
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"

# Start in background (hidden window)
Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden

# Verify it's running
Invoke-WebRequest -Uri "http://localhost:7823/health" | Select-Object -ExpandProperty Content
```

Expected:
```json
{"status": "ok", "db": "C:\\Users\\you\\.claude_memory.db", "memories": 0, "version": "2.1.0"}
```

**Step 2 — Auto-start on login (optional but recommended):**
```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "$env:USERPROFILE\mem_server.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "ClaudeMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest
```

**Step 3 — Install the skill in Claude Desktop:**
Settings → Skills → Add Custom Skill → upload `SKILL.md`

**Step 4 — Use it (same commands as Mac/Linux):**
```
/mem "My Project"
/context my project
/mem list
```

For detailed Windows instructions see [docs/WINDOWS.md](docs/WINDOWS.md).

---

## Commands

| Command | Action |
|---|---|
| `/mem [title]` | Save current conversation. Updates existing memory for this project if one exists — no duplicates. |
| `/mem list` | List all saved memories |
| `/context [query]` | Search and restore memory by topic |
| `/context id:[uuid]` | Retrieve specific memory by ID |
| `/recall [query]` | Alias for `/context` |

---

## What Gets Saved

Not a compressed summary. A complete, lossless record:

- **Summary** (1,500–4,000 words): Full narrative of everything discussed
- **Key decisions**: What was decided, WHY, and what was REJECTED with reasons
- **Open questions**: Specific, actionable next steps
- **Entities**: All named people, products, companies, tools, documents
- **Tags**: Auto-extracted for searchability

A decision without its reasoning is half-useless. A rejected option without its rejection reason is dangerous — future Claude might re-propose it.

---

## Architecture

```
claude-memory-skill/
├── SKILL.md                    Upload this to Claude (auto-detects platform)
├── mem.py                      Mac/Linux: copy to ~/mem.py
├── mem_server.py               Windows: copy to %USERPROFILE%\mem_server.py
├── schema.sql                  SQLite schema reference
├── scripts/
│   ├── start_mem_server.sh     Mac/Linux server startup script
│   ├── start_mem_server.ps1    Windows server startup script
│   ├── setup.sh                Mac/Linux full install script
│   ├── setup.ps1               Windows full install script
│   └── verify.py               End-to-end installation checker
├── references/
│   ├── STORAGE_SPEC.md
│   ├── RETRIEVAL_SPEC.md
│   └── QUALITY_RUBRIC.md
├── examples/
│   ├── example_memory.json
│   ├── example_retrieval.md
│   └── example_workflow.md
├── tests/
│   ├── run_all_tests.py
│   ├── test_connection.py
│   ├── test_storage.py
│   └── test_search.py
└── docs/
    ├── WINDOWS.md              Full Windows setup guide
    ├── SETUP.md                Detailed Mac/Linux guide
    ├── ADVANCED.md             Advanced configuration
    ├── TROUBLESHOOTING.md      Common issues and fixes
    └── API_REFERENCE.md        CLI + HTTP API reference
```

**Storage:** `~/.claude_memory.db` on Mac/Linux · `C:\Users\you\.claude_memory.db` on Windows. SQLite with FTS5 full-text search. Auto-created on first run.

---

## Data Privacy

Your data never leaves your machine. No external services. Delete any memory or the entire database at any time.

```bash
# Back up
cp ~/.claude_memory.db ~/claude_memory_backup.db

# Export all as JSON
python3 ~/mem.py list --limit 10000
```

---

## FAQ

**Does this work on the free Claude plan?**
No. Skills require Pro, Max, Team, or Enterprise.

**Will memories persist across Claude updates?**
Yes. The database is completely independent of Claude. Reinstalling Claude has no effect.

**Can I load more than one memory in a single conversation?**
Yes. Use `/context` multiple times. Claude synthesises them and flags any contradictions. This is one of the most powerful features — reference multiple past conversations without overflowing your context window.

**What happens if I run `/mem` on a project I've already saved?**
It updates the existing record additively. Nothing is lost.

**Why do I need `mem_server.py` on Windows but not Mac?**
Claude Desktop on Windows runs bash_tool inside a Linux container that cannot access your Windows filesystem. `mem_server.py` runs on your real machine and Claude reaches it over HTTP. Mac/Linux bash_tool runs on the real filesystem directly, so no server is needed.

**The server was running but stopped after a reboot. What do I do?**
Add it to Task Scheduler using the command in Step 2 of the Windows Quick Start above.

---

## Troubleshooting

**`mem.py isn't installed yet` (Mac/Linux)**
Run `curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py && python3 ~/mem.py setup` in your own terminal.

**`Connection refused` on Windows**
`mem_server.py` is not running. Open PowerShell and run: `Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden`

**`python3: command not found`**
Install Python 3.8+ from [python.org](https://python.org). On Windows use `python` instead of `python3`.

**`No search results`**
Try simpler terms, then `/mem list` to browse all saved memories.

Full troubleshooting guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Roadmap

- [x] Full-text search (SQLite FTS5)
- [x] Local SQLite storage — zero setup, no accounts
- [x] Upsert logic — one memory per project, no duplicates
- [x] Lossless storage (1,500–4,000 word summaries)
- [x] Multi-memory loading in a single session
- [x] Windows support via local HTTP server
- [ ] Semantic search with local embeddings
- [ ] Export to Markdown and Obsidian
- [ ] Memory merging across projects

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT. See [LICENSE](LICENSE).

---

*Built by [Shiban Banerjee](https://github.com/shibanbanerjee) — Co-Founder and Chief AI Officer at Zyra*
