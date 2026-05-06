# API Reference

Claude Memory exposes two interfaces: a **CLI** (for Mac/Linux direct mode) and an **HTTP API** (for Windows and any platform running `mem_server.py`). Both interfaces are functionally identical — same data, same operations, same responses.

---

## CLI Reference (`mem.py`)

Used on Mac/Linux when `mem.py` is installed at `~/mem.py`.

### `setup`
Initialises the database schema and prints status.
```bash
python3 ~/mem.py setup
```
Output:
```
✅ Claude Memory — local database ready
   Location: /home/you/.claude_memory.db
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
{"title": "...", "project": "...", "summary": "...", ...}
MEMORY_JSON
```
Output:
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
```

### `update`
Reads JSON from stdin and overwrites an existing memory record by ID.
```bash
python3 ~/mem.py update --id "uuid" << 'MEMORY_JSON'
{"title": "...", "project": "...", "summary": "...", ...}
MEMORY_JSON
```
Output:
```json
{"status": "updated", "id": "uuid", "title": "...", "updated_at": "..."}
```

### `search`
Full-text search across title, project, summary, and tags. Falls back to LIKE if FTS returns nothing.
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
python3 ~/mem.py get --id "uuid"
```

---

## HTTP API Reference (`mem_server.py`)

Used on Windows (and optionally on any platform). Server runs on `localhost:7823` by default.

Base URL: `http://localhost:7823` (or `http://host.docker.internal:7823` from inside Claude's container)

All endpoints return `Content-Type: application/json`.

---

### `GET /health`
Server status and memory count.

**Response:**
```json
{
  "status": "ok",
  "db": "/Users/you/.claude_memory.db",
  "memories": 5,
  "version": "2.1.0"
}
```

---

### `GET /setup`
Initialises the database schema (idempotent) and returns status.

**Response:** Same as `/health`.

---

### `GET /check?project=slug`
Checks whether a memory exists for the given project slug.

**Parameters:**
- `project` (required) — project slug string

**Response (exists):**
```json
{
  "exists": true,
  "id": "uuid",
  "title": "...",
  "created_at": "2026-05-06T10:00:00Z",
  "updated_at": "2026-05-06T12:00:00Z"
}
```

**Response (not found):**
```json
{"exists": false}
```

---

### `POST /store`
Inserts a new memory record. Body must be a JSON object with at least `title` and `summary`.

**Request body:**
```json
{
  "title": "Devam Strategy Session — May 2026",
  "project": "devam-strategy",
  "conversation_url": "",
  "tags": ["devam", "strategy", "product"],
  "summary": "1500-4000 word narrative...",
  "key_decisions": ["Decision 1 — reason", "Decision 2 — reason"],
  "open_questions": ["What is the next step for X?"],
  "entities": {
    "people": ["Shiban — CTO"],
    "products": ["Devam", "Prasad"],
    "companies": ["Zyra"],
    "concepts": ["faith economy", "SCE"],
    "documents": ["Devam_Vision_Strategy.docx"]
  },
  "token_count_est": 0
}
```

**Response:**
```json
{
  "status": "stored",
  "id": "new-uuid",
  "title": "Devam Strategy Session — May 2026",
  "created_at": "2026-05-06T14:30:00Z"
}
```

**curl example:**
```bash
curl -X POST http://localhost:7823/store \
  -H "Content-Type: application/json" \
  -d '{"title": "...", "project": "...", "summary": "..."}'
```

---

### `POST /update?id=uuid`
Overwrites an existing memory record. Same body shape as `/store`.

**Parameters:**
- `id` (required) — UUID of the memory to update

**Response:**
```json
{
  "status": "updated",
  "id": "uuid",
  "title": "...",
  "updated_at": "2026-05-06T15:00:00Z"
}
```

**Response (not found):**
```json
{"status": "not_found", "id": "uuid"}
```
HTTP status 404.

---

### `GET /search?query=term&limit=5&project=optional`
Full-text search. Falls back to LIKE search if FTS returns nothing.

**Parameters:**
- `query` (required) — search terms
- `limit` (optional, default 5) — max results
- `project` (optional) — filter to specific project

**Response:**
```json
{
  "status": "found",
  "count": 2,
  "memories": [{...full memory object...}, {...}]
}
```
or
```json
{"status": "no_results", "query": "your query"}
```

---

### `GET /list?limit=20&project=optional`
Lists all memories ordered by most recently updated.

**Parameters:**
- `limit` (optional, default 20)
- `project` (optional) — filter to specific project

**Response:**
```json
{
  "count": 5,
  "memories": [
    {
      "id": "uuid",
      "created_at": "...",
      "updated_at": "...",
      "title": "...",
      "project": "...",
      "tags": [...],
      "token_count_est": 312,
      "conversation_url": ""
    }
  ]
}
```

---

### `GET /get?id=uuid`
Returns a single full memory record.

**Parameters:**
- `id` (required) — UUID

**Response:** Full memory object including all fields.

**Response (not found):**
```json
{"status": "not_found", "id": "uuid"}
```
HTTP status 404.

---

## Memory Object Schema

All endpoints that return memories use this structure:

```json
{
  "id": "uuid-v4",
  "created_at": "2026-05-06T10:00:00Z",
  "updated_at": "2026-05-06T12:00:00Z",
  "title": "Short descriptive title (max 100 chars)",
  "project": "project-slug",
  "conversation_url": "https://claude.ai/chat/... or empty string",
  "summary": "1500-4000 word lossless narrative",
  "key_decisions": ["Decision — reasoning", "..."],
  "open_questions": ["Specific actionable question", "..."],
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

---

## Server Configuration

```bash
# Custom port
python3 ~/mem_server.py --port 8080

# Restrict to loopback only (more secure, but Claude's container can't reach it)
python3 ~/mem_server.py --host 127.0.0.1

# Default: listen on all interfaces, port 7823
python3 ~/mem_server.py
```
