# 🧠 Claude Memory Skill

> **Persistent, searchable memory for Claude — stored locally on your machine.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Skills](https://img.shields.io/badge/Claude-Skill-blueviolet)](https://github.com/anthropics/skills)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![SQLite](https://img.shields.io/badge/Storage-SQLite-green)](https://sqlite.org)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Claude's context window resets with every new conversation. This skill gives Claude a **persistent memory layer** — so your long-running projects, key decisions, and working context are never lost.

**Type `/mem` to save. Type `/context` to restore.**

No accounts. No configuration. No external services. Everything stays on your machine.

---

## The Problem This Solves

You spend three hours in a deep product brainstorm with Claude. Fifteen critical decisions. Four frameworks applied. A full strategy mapped with nuance that took hours to develop. Then you open a new conversation — and Claude knows nothing.

Claude Memory fixes this. One command saves everything. One command restores it in any future session, in any conversation.

---

## How It Works

```
Your Conversation (hours of work)
         |
         |  /mem "My Project"
         v
Claude Memory Skill
  1. Checks existing memories for this project
  2. Reads the ENTIRE conversation from start to finish
  3. Generates detailed summary (1,500–4,000 words)
  4. Extracts: decisions + WHY, rejected ideas,
     open questions, entities, tags
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
Claude, fully restored
"Resuming your project. Last session you completed X.
15 decisions locked. Next step: Y. Where to start?"
```

---

## Quick Start

**Requires: Python 3.8+** — no additional packages, no pip installs, nothing beyond what Python ships with.

### 1. Install the Python helper

```bash
# Mac / Linux
cp scripts/mem.py ~/mem.py

# Windows PowerShell
Copy-Item scripts\mem.py "$env:USERPROFILE\mem.py"
```

### 2. Install the skill

**Claude Code:**
```bash
mkdir -p ~/.claude/skills/claude-memory
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md
```

**Claude.ai:** Settings → Skills → Upload Custom Skill → select `SKILL.md`

### 3. Verify

```bash
python3 ~/mem.py setup
```

Expected output:
```
✅ Claude Memory — local database ready
   Location: /home/you/.claude_memory.db
   Memories stored: 0
```

### 4. Use it

```
/mem "My Project"      # Save current conversation
/context my project    # Restore in any future session
/mem list              # Browse all saved memories
```

The database is created automatically on first use. There is nothing else to configure.

---

## Commands

| Command | Action |
|---|---|
| `/mem [title]` | Save current conversation to memory. If a memory for this project already exists, updates it instead of creating a duplicate. |
| `/mem list` | List all saved memories |
| `/context [query]` | Search and restore by topic |
| `/context id:[uuid]` | Retrieve specific memory by ID |
| `/recall [query]` | Alias for `/context` |

---

## What Gets Saved

Claude Memory captures everything that matters — not a compressed summary that loses nuance, but a complete detailed record:

- **Summary** (1,500–4,000 words): Full narrative of everything discussed
- **Key decisions**: What was decided, WHY, and what was REJECTED with reasons
- **Open questions**: Specific, actionable next steps
- **Entities**: All named people, products, companies, tools, documents
- **Tags**: Auto-extracted for searchability

Most memory tools compress aggressively. This one does not. A decision without its reasoning is half-useless. A rejected option without its rejection reason is actively dangerous — future Claude might re-propose it. A few hundred extra words in the database costs nothing. A lost decision costs everything.

---

## Architecture

```
claude-memory-skill/
├── SKILL.md                    Core skill — Claude reads this
├── scripts/
│   ├── mem.py                  Python CLI helper (copy to ~/mem.py)
│   ├── schema.sql              SQLite schema reference
│   └── verify.py               Checks your installation
├── references/
│   ├── STORAGE_SPEC.md         Storage field specifications
│   ├── RETRIEVAL_SPEC.md       Retrieval and ranking logic
│   └── QUALITY_RUBRIC.md       Good vs bad memory standards
├── examples/
│   ├── example_memory.json     Sample stored memory
│   ├── example_retrieval.md    Sample retrieval session
│   └── example_workflow.md     End-to-end walkthrough
├── tests/
│   ├── run_all_tests.py        Test runner
│   ├── test_connection.py      Test SQLite connectivity
│   ├── test_storage.py         Test write and read
│   └── test_search.py          Test FTS5 search quality
└── docs/
    ├── SETUP.md                Detailed setup guide
    ├── WINDOWS.md              Windows-specific instructions
    ├── ADVANCED.md             Advanced configuration
    ├── TROUBLESHOOTING.md      Common issues and fixes
    └── API_REFERENCE.md        CLI and schema reference
```

**Storage:** All memories are stored in `~/.claude_memory.db` — a single SQLite file on your local machine. The database is created automatically on first use. Full-text search is powered by SQLite's built-in FTS5 engine, with triggers that keep the search index in sync on every write.

---

## Data Privacy

Your data never leaves your machine. All memories are stored in a local SQLite database. No data is sent to any external service. You can delete any memory or the entire database at any time.

**Back up your memories:**
```bash
cp ~/.claude_memory.db ~/claude_memory_backup.db
```

**Export all memories as JSON:**
```bash
python3 ~/mem.py list --limit 10000
```

---

## Roadmap

- [x] Full-text search (SQLite FTS5)
- [x] Local SQLite storage — zero setup, no accounts
- [x] Upsert logic — one memory per project, no duplicates
- [x] Detailed storage with quality standards
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
