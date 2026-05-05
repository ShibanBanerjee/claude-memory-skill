# Architecture — How claude-memory-skill Works

## Overview

The skill has three layers that work together:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: SKILL.md (Behaviour Definition)                   │
│  Tells Claude what /mem and /context mean and how to        │
│  execute them. Loaded into Claude's context when triggered. │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Database Operations                               │
│                                                             │
│  Path A: Supabase MCP (when Claude has MCP access)          │
│  → Direct SQL via execute_sql tool                          │
│  → No REST API, no IP restrictions, most reliable           │
│                                                             │
│  Path B: mem.py (Python CLI helper)                         │
│  → REST API calls to Supabase PostgREST                     │
│  → Used from user's local machine                           │
│  → Requires legacy anon key (not publishable key)           │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Supabase PostgreSQL                               │
│                                                             │
│  claude_memories table                                      │
│  ├── UUID primary key                                       │
│  ├── JSONB fields: key_decisions, open_questions, entities  │
│  ├── TEXT[]: tags (with GIN index)                          │
│  ├── TSVECTOR: search_vector (full-text search)             │
│  └── TIMESTAMPTZ: created_at                                │
└─────────────────────────────────────────────────────────────┘
```

---

## The Memory Generation Process

When you type `/mem`, Claude performs the following steps:

### 1. Context Window Read
Claude reads the entire current conversation from the beginning — every message, every decision, every rejected idea, every number mentioned.

### 2. Structured Extraction
Claude generates a structured JSON object with these components:

**Summary (1,500–4,000 words):**
Not a compression. A detailed narrative that captures:
- What the project is
- All key concepts and how they were defined
- Every decision made and the reasoning behind it
- Every idea rejected and why it was rejected
- All specific numbers, names, dates
- Current status and next steps
- Any standing instructions from the user

**Key Decisions:**
Each decision is a complete statement: what was decided + why + what alternative was rejected. These are the load-bearing facts future Claude needs to not re-open settled debates.

**Open Questions:**
Specific, actionable questions with enough context to understand without re-reading the full summary. The agenda for future sessions.

**Entities:**
Structured catalogue of people, products, companies, concepts, and documents referenced.

### 3. Storage
Via Supabase MCP (direct SQL insert) or mem.py (REST API).

### 4. Confirmation
Claude confirms with the memory ID, decision count, and the exact command to restore it.

---

## The Retrieval Process

When you type `/context [query]`:

### 1. Full-Text Search
PostgreSQL's `tsvector` full-text search runs against title, project, summary, and tags simultaneously.

### 2. Fallback Searches
If FTS returns no results: tag array match → project name match → list all recent.

### 3. Context Injection
The retrieved memory — summary, decisions, questions, entities — is loaded into Claude's working context. Claude treats it as fully known background, exactly as if the original conversation just happened.

### 4. Orientation
Claude gives a one-sentence orientation of where things stand and invites you to continue.

---

## Why Two Storage Paths?

**Supabase MCP (Path A)** is used when Claude is running in its sandbox environment (claude.ai). The MCP connection is authenticated at the platform level and bypasses IP restrictions. This is the preferred path.

**mem.py REST (Path B)** is used when running from a local machine. It calls Supabase's PostgREST API directly. Requires the legacy anon key (not the new publishable key, which is browser-only and requires domain whitelisting).

---

## Database Schema Design Decisions

**Why JSONB for decisions and questions?**
Allows rich querying (e.g., `jsonb_array_length(key_decisions) > 10`) while preserving the list structure. Future versions could index into individual decisions for semantic search.

**Why TEXT[] for tags?**
GIN index on arrays enables fast `&&` (overlap) queries: "find memories tagged both 'backend' AND 'architecture'". More performant than JSONB for simple string matching.

**Why TSVECTOR trigger (not generated column)?**
PostgreSQL's `to_tsvector()` is not immutable (it depends on the search configuration), so it cannot be used in generated columns. A trigger fires on INSERT/UPDATE and populates the column, achieving the same result.

**Why not pgvector (semantic search)?**
Full-text search covers the primary use case: finding memories by topic and keyword. Semantic search (finding memories by meaning even when keywords differ) is a valuable V2 enhancement but adds operational complexity (embedding generation, vector dimensions, index tuning). The foundation is designed to support pgvector — the column can be added without schema changes.

---

## Security Model

- Database lives in your own Supabase project — no shared infrastructure
- RLS (Row Level Security) is enabled with a permissive policy for personal use
- Credentials live in `~/.claude_memory_config.json` — local only, never transmitted
- For team use: replace the permissive policy with user-scoped policies based on JWT claims
- The publishable key is intentionally not used for server-side scripts (it requires domain whitelisting, designed for browser use)
