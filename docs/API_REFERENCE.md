# API Reference

Claude Memory exposes two interfaces: the **Supabase MCP** (for Claude environments with MCP configured) and the **mem.py CLI** (REST-based Python helper for other environments). Both interfaces operate against the same Supabase PostgreSQL database.

---

## Supabase MCP — SQL Reference

Used when the Supabase MCP (`execute_sql`) tool is available. Claude runs these SQL statements directly.

### Check if a project memory exists

```sql
SELECT id, title, created_at, updated_at
FROM claude_memories
WHERE project = 'project-slug'
ORDER BY updated_at DESC
LIMIT 1;
```

### Store a new memory

```sql
INSERT INTO claude_memories
  (title, project, conversation_url, summary,
   key_decisions, open_questions, entities, tags, token_count_est)
VALUES (
  'Title here',
  'project-slug',
  '',
  'Full summary text...',
  '["Decision 1 — reason", "Decision 2 — reason"]'::jsonb,
  '["Open question 1"]'::jsonb,
  '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  ARRAY['tag1', 'tag2', 'tag3'],
  450
)
RETURNING id, title, created_at;
```

### Update an existing memory

```sql
UPDATE claude_memories SET
  updated_at       = NOW(),
  title            = 'Updated title',
  summary          = 'Updated summary...',
  key_decisions    = '["Decision 1", "Decision 2"]'::jsonb,
  open_questions   = '["Open question 1"]'::jsonb,
  entities         = '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  tags             = ARRAY['tag1', 'tag2'],
  token_count_est  = 450
WHERE id = 'uuid-here'
RETURNING id, title, updated_at;
```

### Search by full-text

```sql
SELECT id, title, project, updated_at, tags, LEFT(summary, 300) AS preview
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'search terms here')
ORDER BY updated_at DESC
LIMIT 5;
```

### List recent memories

```sql
SELECT id, title, project, created_at, updated_at, tags, token_count_est
FROM claude_memories
ORDER BY updated_at DESC
LIMIT 20;
```

### Get by ID

```sql
SELECT * FROM claude_memories WHERE id = 'uuid-here';
```

---

## mem.py CLI Reference

Used when Supabase MCP is not available. Requires Python 3.8+, `pip install requests`, and `~/.claude_memory_config.json`.

### `setup`
Verifies the Supabase connection and reports memory count.
```bash
python3 ~/mem.py setup
```
Output:
```
Claude Memory — Supabase ready
   Project: https://your-project.supabase.co
   Memories stored: 3
```

### `check`
Returns whether a memory exists for a given project slug.
```bash
python3 ~/mem.py check --project "project-slug"
```
Output (exists):
```json
{"exists": true, "id": "uuid", "title": "...", "created_at": "...", "updated_at": "..."}
```
Output (not found):
```json
{"exists": false}
```

### `store`
Reads JSON from stdin and inserts a new memory record.
```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{
  "title": "...",
  "project": "project-slug",
  "summary": "...",
  "tags": ["tag1", "tag2"],
  "key_decisions": ["Decision — reason — rejected alternative"],
  "open_questions": ["Specific open question with context"],
  "entities": {"people": [], "products": [], "companies": [], "concepts": [], "documents": []},
  "token_count_est": 0
}
MEMORY_JSON
```
Output:
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
```

### `update`
Reads JSON from stdin and overwrites an existing memory record by ID.
```bash
python3 ~/mem.py update --id "uuid-here" << 'MEMORY_JSON'
{ ...same structure as store... }
MEMORY_JSON
```
Output:
```json
{"status": "updated", "id": "uuid", "title": "...", "updated_at": "..."}
```

### `search`
Full-text search via `search_vector`. Falls back to LIKE if FTS returns nothing.
```bash
python3 ~/mem.py search --query "devam strategy" --limit 5
python3 ~/mem.py search --query "devam" --project "devam-strategy" --limit 3
```
Output:
```json
{"status": "found", "count": 2, "memories": [...]}
{"status": "no_results", "query": "..."}
```

### `list`
Lists all memories ordered by most recently updated.
```bash
python3 ~/mem.py list --limit 20
python3 ~/mem.py list --project "devam-strategy" --limit 5
```
Output:
```json
{"count": 3, "memories": [{...}, {...}, {...}]}
```

### `get`
Retrieves a single full memory record by UUID.
```bash
python3 ~/mem.py get --id "uuid-here"
```

---

## Memory Object Schema

All operations use this structure:

```json
{
  "id": "uuid-v4",
  "created_at": "2026-05-06T10:00:00Z",
  "updated_at": "2026-05-06T12:00:00Z",
  "title": "Short descriptive title (max 100 chars)",
  "project": "project-slug",
  "conversation_url": "https://claude.ai/chat/... or empty string",
  "summary": "1500-4000 word lossless narrative",
  "key_decisions": ["Decision — reasoning — rejected alternative", "..."],
  "open_questions": ["Specific actionable question with context", "..."],
  "entities": {
    "people": ["Name — Role"],
    "products": ["Product name"],
    "companies": ["Company name"],
    "concepts": ["Framework or methodology"],
    "documents": ["Document title"]
  },
  "tags": ["tag1", "tag2", "tag3"],
  "token_count_est": 312
}
```
