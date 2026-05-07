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
│  Layer 2: Storage Backend                                   │
│                                                             │
│  Primary — Supabase MCP (execute_sql tool)                  │
│  → Claude runs SQL directly against PostgreSQL              │
│  → No local files required                                  │
│  → Works on every platform including Windows                │
│                                                             │
│  Fallback — mem.py + Supabase REST API                      │
│  → Python script calls PostgREST endpoints                  │
│  → Credentials in ~/.claude_memory_config.json              │
│  → Requires pip install requests                            │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  Supabase PostgreSQL                                        │
│  → claude_memories table                                    │
│  → JSONB fields (key_decisions, open_questions, entities)   │
│  → TEXT[] tags with GIN index                               │
│  → TSVECTOR trigger for full-text search                    │
└─────────────────────────────────────────────────────────────┘
```

---

## The Memory Generation Process

When you type `/mem`, Claude performs the following steps:

### 1. Context Window Read
Claude reads the entire current conversation from the beginning — every message, every decision, every rejected idea, every number mentioned.

### 2. Project Check
Claude queries the database to determine whether a memory already exists for this project slug. If one does, the existing record is updated. If not, a new record is inserted.

**MCP path:** `SELECT id FROM claude_memories WHERE project = 'slug' ORDER BY updated_at DESC LIMIT 1`
**REST path:** `python3 ~/mem.py check --project "slug"`

### 3. Structured Extraction
Claude generates a structured JSON object with:

**Summary (1,500–4,000 words):** A detailed narrative capturing the project overview, all key concepts and definitions, every decision made and the reasoning behind it, every idea rejected and why, all specific numbers and names, current status, and any standing instructions from the user.

**Key Decisions:** Each decision is a complete statement — what was decided, why, and what alternative was rejected. These are the load-bearing facts that prevent future Claude from re-opening settled debates.

**Open Questions:** Specific, actionable questions with enough context to understand without re-reading the full summary. The agenda for future sessions.

**Entities:** Structured catalogue of people, products, companies, concepts, and documents referenced.

### 4. Storage
The JSON is written to Supabase via SQL INSERT (MCP) or the PostgREST API (mem.py). The `BEFORE INSERT OR UPDATE` trigger automatically populates the `search_vector` TSVECTOR column from title, project, summary, and tags.

### 5. Confirmation
Claude confirms with the memory ID, decision count, and the exact command to restore it.

---

## The Retrieval Process

When you type `/context [query]`:

### 1. Full-Text Search
PostgreSQL searches the `search_vector` TSVECTOR column using `plainto_tsquery`. This tokenises the query and finds memories where the indexed text matches. Results are ordered by `updated_at DESC`.

### 2. Fallback Search
If FTS returns no results, `mem.py` falls back to a PostgREST `ilike` query across title, project, and summary. This catches short queries or unusual terms that don't tokenise well.

### 3. Context Injection
The retrieved memory — summary, decisions, questions, entities — is loaded into Claude's working context. Claude treats it as fully known background.

### 4. Orientation
Claude gives a one-sentence orientation of where things stand and invites you to continue.

---

## Database Design

**Why Supabase PostgreSQL?**
Supabase provides a managed PostgreSQL instance accessible via REST (PostgREST) and direct SQL (via MCP). The MCP path means Claude can store and retrieve memories from any device — including Windows Claude Desktop, which runs bash commands inside an isolated Linux container that can't reach the local Windows filesystem.

**Why JSONB for arrays and objects?**
JSONB allows structured storage of key_decisions, open_questions, and entities without needing separate tables. PostgreSQL's JSONB operators and GIN indexes make these fields queryable efficiently.

**Why TEXT[] for tags?**
Native PostgreSQL arrays allow GIN index-based lookups like `'tag' = ANY(tags)` and PostgREST filter syntax, while keeping the data normalised without a junction table.

**Why TSVECTOR with a trigger?**
The `search_vector` column is populated by a `BEFORE INSERT OR UPDATE` trigger that calls `to_tsvector('english', ...)` across title, project, summary, and tags. This approach is more reliable than a generated column (which would require `to_tsvector` to be immutable) and keeps the FTS index current automatically on every write.

---

## Security and Privacy

- All data lives in your own Supabase project — you own the database
- The anon key gives read/write access to the `claude_memories` table; enable Row Level Security for finer-grained control
- The credentials file (`~/.claude_memory_config.json`) is in your `.gitignore` and should never be committed
- Delete records from the Supabase Table Editor or via SQL at any time
