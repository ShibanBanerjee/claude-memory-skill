# mem.py Quick Reference

All Claude memory operations go through `mem.py`. The script reads JSON from stdin and writes JSON to stdout. The database lives at `~/.claude_memory.db` and is created automatically on first use.

---

## Check if a project memory exists

```bash
python3 ~/mem.py check --project "project-slug"
```

Returns `{"exists": true, "id": "...", ...}` or `{"exists": false}`.

---

## Store a new memory

```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{
  "title": "...",
  "project": "project-slug",
  "summary": "...",
  "tags": ["tag1", "tag2"],
  "key_decisions": ["Decision 1 — reason — rejected alternative"],
  "open_questions": ["Specific open question with context"],
  "entities": {"people": [], "products": [], "companies": [], "concepts": [], "documents": []},
  "token_count_est": 0
}
MEMORY_JSON
```

---

## Update an existing memory

```bash
python3 ~/mem.py update --id "uuid-here" << 'MEMORY_JSON'
{
  "title": "...",
  "project": "project-slug",
  "summary": "...",
  "tags": [...],
  "key_decisions": [...],
  "open_questions": [...],
  "entities": {...},
  "token_count_est": 0
}
MEMORY_JSON
```

---

## Search memories

```bash
python3 ~/mem.py search --query "search terms here" --limit 5
python3 ~/mem.py search --query "auth decisions" --project "backend" --limit 3
```

---

## List recent memories

```bash
python3 ~/mem.py list --limit 20
python3 ~/mem.py list --project "my-project" --limit 10
```

---

## Get by ID

```bash
python3 ~/mem.py get --id "uuid-here"
```

---

## Initialise / status check

```bash
python3 ~/mem.py setup
```
