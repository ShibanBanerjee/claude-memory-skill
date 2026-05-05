# Architecture — How claude-memory-skill Works

## Overview

The skill has two layers that work together:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: SKILL.md (Behaviour Definition)                   │
│  Tells Claude what /mem and /context mean and how to        │
│  execute them. Loaded into Claude's context when triggered. │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: mem.py + SQLite                                   │
│                                                             │
│  mem.py — Python CLI helper (stdlib only, no deps)          │
│  → Receives JSON from Claude via stdin                      │
│  → Reads and writes ~/.claude_memory.db                     │
│  → Returns JSON results to Claude via stdout                │
│                                                             │
│  ~/.claude_memory.db — SQLite database                      │
│  → claude_memories table                                    │
│  → FTS5 virtual table for full-text search                  │
│  → Triggers keep FTS index in sync automatically            │
└─────────────────────────────────────────────────────────────┘
```

---

## The Memory Generation Process

When you type `/mem`, Claude performs the following steps:

### 1. Context Window Read
Claude reads the entire current conversation from the beginning — every message, every decision, every rejected idea, every number mentioned.

### 2. Project Check
Claude runs `python3 ~/mem.py check --project "project-slug"` to determine whether a memory already exists for this project. If one does, the existing record is updated. If not, a new record is inserted.

### 3. Structured Extraction
Claude generates a structured JSON object with these components:

**Summary (1,500–4,000 words):**
A detailed narrative capturing what the project is, all key concepts and definitions, every decision made and the reasoning behind it, every idea rejected and why, all specific numbers and names, current status, and any standing instructions from the user.

**Key Decisions:**
Each decision is a complete statement: what was decided + why + what alternative was rejected. These are the load-bearing facts future Claude needs to not re-open settled debates.

**Open Questions:**
Specific, actionable questions with enough context to understand without re-reading the full summary. The agenda for future sessions.

**Entities:**
Structured catalogue of people, products, companies, concepts, and documents referenced.

### 4. Storage
JSON is piped to `mem.py store` (new memory) or `mem.py update --id` (existing memory).

### 5. Confirmation
Claude confirms with the memory ID, decision count, and the exact command to restore it.

---

## The Retrieval Process

When you type `/context [query]`:

### 1. Full-Text Search
SQLite FTS5 searches across title, project, summary, and tags simultaneously. The FTS5 engine tokenises and indexes all text fields. Results are ranked by recency.

### 2. Fallback Search
If FTS5 returns no results, `mem.py` falls back to a LIKE search across title, project, and summary. This catches cases where the search term is too short or unusual for the FTS tokeniser.

### 3. Context Injection
The retrieved memory — summary, decisions, questions, entities — is loaded into Claude's working context. Claude treats it as fully known background, exactly as if the original conversation just happened.

### 4. Orientation
Claude gives a one-sentence orientation of where things stand and invites you to continue.

---

## Database Design

**Why SQLite?**
SQLite is part of Python's standard library. No installation, no account, no configuration. The entire database is a single file at `~/.claude_memory.db`, trivially backed up by copying the file.

**Why FTS5 for full-text search?**
SQLite's FTS5 extension provides tokenised, multi-column full-text search. Three triggers (INSERT, UPDATE, DELETE) keep the FTS index in sync with the main table automatically — no manual rebuilds, no staleness.

**Why JSON stored as TEXT?**
SQLite doesn't have a native JSONB type. Array and object fields (key_decisions, open_questions, entities, tags) are stored as JSON strings and deserialised by `mem.py` before returning results. This preserves rich structure while keeping the schema portable.

**Why WAL mode?**
Write-Ahead Logging makes writes safer under concurrent access and allows reads to proceed simultaneously with writes. Relevant when Claude and a terminal session are both accessing the database.

---

## Security and Privacy

- All data lives on your local machine in `~/.claude_memory.db`
- No credentials, no API keys, no network connections of any kind
- Delete the file at any time to wipe all memories completely
- Back up by copying the file anywhere you like
