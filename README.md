# 🧠 Claude Memory Skill

> **Persistent, searchable, long-term memory for Claude — stored in your own database.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Skills](https://img.shields.io/badge/Claude-Skill-blueviolet)](https://github.com/anthropics/skills)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)
[![Version](https://img.shields.io/badge/version-1.2.0-blue)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Claude's context window resets with every new conversation. This skill gives Claude a **persistent memory layer** — so your long-running projects, key decisions, and working context are never lost.

**Type `/mem` to save. Type `/context` to restore.**

---

## The Problem This Solves

You spend 3 hours in a deep product brainstorm with Claude. 15 critical decisions. 4 frameworks applied. A full strategy mapped with nuance that took hours to develop. Then you open a new conversation — and Claude knows nothing.

Claude Memory fixes this. One command saves everything. One command restores it in any future session, on any device, in any conversation.

---

## How It Works

```
Your Conversation (hours of work)
         |
         |  /mem "Project Name"
         v
Claude Memory Skill
  1. Checks existing memories for this project
  2. Reads the ENTIRE conversation from start
  3. Generates detailed summary (1,500-4,000 words)
  4. Extracts: decisions + WHY, open questions,
     instructions, entities, tags
  5. Stores in YOUR Supabase database
         |
         v
Your Supabase Database (PostgreSQL + FTS + pgvector ready)
Your data. Your database. Your control.
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

### 1. Set up Supabase (5 minutes)

Create a free project at supabase.com, open the SQL Editor, and run `scripts/schema.sql`.

### 2. Configure credentials

**Mac/Linux:**
```bash
cat > ~/.claude_memory_config.json << 'EOF'
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "YOUR_LEGACY_ANON_KEY"
}
EOF
```

**Windows PowerShell:**
```powershell
@'
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "YOUR_LEGACY_ANON_KEY"
}
'@ | Out-File -FilePath "$env:USERPROFILE\.claude_memory_config.json" -Encoding utf8
```

Get your key from: Supabase Dashboard -> Settings -> API Keys -> Legacy anon tab.

### 3. Install the Python helper

```bash
pip install requests --break-system-packages
cp scripts/mem.py ~/mem.py
python3 ~/mem.py setup
```

### 4. Install the skill

```bash
# Claude Code
cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md

# Claude.ai — upload via Settings -> Skills -> Upload Custom Skill
```

### 5. Use it

```
/mem "My Project"          # Save current conversation
/context my project        # Restore in any future session
/mem list                  # Browse all memories
```

---

## Commands

| Command | Action |
|---|---|
| `/mem [title]` | Save current conversation to memory |
| `/mem update` | Update existing memory with new content |
| `/mem list` | List all saved memories |
| `/context [query]` | Search and restore by topic |
| `/context id:[uuid]` | Retrieve specific memory by ID |
| `/recall [query]` | Alias for /context |

---

## What Gets Saved

Claude Memory captures everything that matters — not a compressed summary that loses nuance, but a complete detailed record:

- **Summary** (1,500-4,000 words): Full narrative of everything discussed
- **Key decisions**: What was decided, WHY, and what was REJECTED with reasons
- **Open questions**: Specific, actionable next steps
- **Instructions**: Your preferences and directives to Claude
- **Entities**: All named people, products, companies, tools, documents
- **Tags**: Auto-extracted for searchability

Most memory tools compress aggressively. We do not. A decision without its reasoning is half-useless. A rejected option without its rejection reason is actively dangerous — future Claude might re-propose it. A few hundred extra words in the database costs nothing. A lost decision costs everything.

---

## Architecture

```
claude-memory-skill/
├── SKILL.md                    Core skill — Claude reads this
├── scripts/
│   ├── mem.py                  Python CLI helper
│   ├── schema.sql              Supabase database schema
│   ├── schema_pgvector.sql     Optional semantic search
│   └── migrate_v1_v2.sql       Migration scripts
├── references/
│   ├── STORAGE_SPEC.md         Storage field specifications
│   ├── RETRIEVAL_SPEC.md       Retrieval and ranking logic
│   ├── QUALITY_RUBRIC.md       Good vs bad memory standards
│   └── MCP_REFERENCE.md        Supabase MCP reference
├── examples/
│   ├── example_memory.json     Sample stored memory
│   ├── example_retrieval.md    Sample retrieval session
│   └── example_workflow.md     End-to-end walkthrough
├── tests/
│   ├── test_connection.py      Test Supabase connectivity
│   ├── test_storage.py         Test write and read
│   ├── test_search.py          Test FTS quality
│   └── test_quality.py         Validate memory standards
├── docs/
│   ├── SETUP.md                Detailed setup guide
│   ├── WINDOWS.md              Windows-specific instructions
│   ├── ADVANCED.md             pgvector and advanced config
│   ├── TROUBLESHOOTING.md      Common issues and fixes
│   └── API_REFERENCE.md        Full schema and API docs
└── .github/
    ├── workflows/
    │   └── validate-skill.yml  CI validation
    └── ISSUE_TEMPLATE/
        ├── bug_report.md
        └── feature_request.md
```

---

## Data Privacy

Your data never leaves your control. All memories are stored in your own Supabase database. No data is sent to any third-party service. You can delete any memory at any time. Self-host Supabase for complete air-gap privacy.

---

## Roadmap

- [x] Full-text search (PostgreSQL FTS)
- [x] Supabase MCP integration
- [x] Local Python CLI
- [x] Detailed storage with quality standards
- [ ] pgvector semantic search
- [ ] Auto-checkpoint every N messages
- [ ] Memory merging across sessions
- [ ] Team shared memories with RLS
- [ ] Export to Markdown and Obsidian

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT. See [LICENSE](LICENSE).

---

*Built by [Shiban Banerjee](https://github.com/shibanbanerjee) — Co-Founder and Chief AI Officer at Zyra*
