# API Reference

## Database Schema

### claude_memories

| Column | Type | Description |
|---|---|---|
| id | TEXT | UUID primary key, auto-generated |
| created_at | TEXT | ISO 8601 UTC timestamp — when memory was first saved |
| updated_at | TEXT | ISO 8601 UTC timestamp — when memory was last updated |
| title | TEXT (required) | Descriptive title |
| project | TEXT | Project or domain slug for grouping and upsert matching |
| conversation_url | TEXT | URL to the original conversation, if known |
| summary | TEXT (required) | Full detailed narrative (1,500–4,000 words) |
| key_decisions | TEXT | JSON array of decision strings with reasoning |
| open_questions | TEXT | JSON array of specific actionable questions |
| entities | TEXT | JSON object: {people, products, companies, concepts, documents} |
| tags | TEXT | JSON array of searchable keyword strings |
| token_count_est | INTEGER | Approximate word count of summary |

### claude_memories_fts (virtual table)

FTS5 virtual table indexing `title`, `project`, `summary`, and `tags`. Kept in sync automatically via triggers on insert, update, and delete.

---

## mem.py CLI Reference

All commands output JSON to stdout. Errors are written to stderr.

### setup

```bash
python3 ~/mem.py setup
```

Initialises the database schema (creates the file and tables if they don't exist) and prints the current memory count.

### check

```bash
python3 ~/mem.py check --project "project-slug"
```

Returns whether a memory exists for the given project slug. Used by Claude before storing to decide insert vs update.

**Output — found:**
```json
{"exists": true, "id": "uuid", "title": "...", "created_at": "...", "updated_at": "..."}
```

**Output — not found:**
```json
{"exists": false}
```

### store

```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{"title": "...", "project": "...", "summary": "...", ...}
MEMORY_JSON
```

Reads a memory JSON object from stdin and inserts a new record. Required fields: `title`, `summary`.

**Output:**
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
```

### update

```bash
python3 ~/mem.py update --id <uuid> << 'MEMORY_JSON'
{"title": "...", "project": "...", "summary": "...", ...}
MEMORY_JSON
```

Reads a memory JSON object from stdin and updates the record with the given ID.

**Output:**
```json
{"status": "updated", "id": "uuid", "title": "...", "updated_at": "..."}
```

### search

```bash
python3 ~/mem.py search --query "search terms" [--project "slug"] [--limit N]
```

Full-text search using FTS5. Falls back to LIKE search if FTS5 returns no results. Default limit: 5.

**Output:**
```json
{"status": "found", "count": 2, "memories": [...]}
```

### list

```bash
python3 ~/mem.py list [--project "slug"] [--limit N]
```

Lists memories in reverse chronological order. Default limit: 20.

**Output:**
```json
{"count": 5, "memories": [...]}
```

### get

```bash
python3 ~/mem.py get --id <uuid>
```

Retrieves a single memory by UUID. Exits with code 1 if not found.
