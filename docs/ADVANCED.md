# Advanced Configuration

## Database Location

By default, the database is created at `~/.claude_memory.db`. This is set at the top of `mem.py`:

```python
DB_PATH = Path.home() / ".claude_memory.db"
```

To use a different location, edit this line before copying `mem.py` to your home directory.

---

## Backup and Restore

The entire memory store is a single SQLite file. Back it up with a standard file copy:

```bash
# Backup
cp ~/.claude_memory.db ~/backups/claude_memory_$(date +%Y%m%d).db

# Restore
cp ~/backups/claude_memory_20260101.db ~/.claude_memory.db
```

On Windows:
```powershell
Copy-Item "$env:USERPROFILE\.claude_memory.db" "$env:USERPROFILE\backups\claude_memory_backup.db"
```

---

## Exporting Memories

Export all memories as JSON:

```bash
python3 ~/mem.py list --limit 10000 > memories_export.json
```

---

## Inspecting the Database Directly

The `.db` file is a standard SQLite database. Open it with any SQLite browser or the `sqlite3` CLI:

```bash
sqlite3 ~/.claude_memory.db
```

Useful queries:

```sql
-- Count all memories
SELECT COUNT(*) FROM claude_memories;

-- List memories by project
SELECT id, title, created_at FROM claude_memories WHERE project = 'my-project';

-- Full-text search
SELECT title, project FROM claude_memories_fts WHERE claude_memories_fts MATCH 'architecture';

-- Manual keyword search
SELECT title, project FROM claude_memories WHERE summary LIKE '%auth service%';
```

---

## Rebuilding the FTS Index

If the full-text search index becomes out of sync (unusual, but possible after a crash mid-write), rebuild it:

```bash
sqlite3 ~/.claude_memory.db "INSERT INTO claude_memories_fts(claude_memories_fts) VALUES('rebuild');"
```

---

## Semantic Search (Roadmap)

The current FTS5 search finds memories by keyword. A planned future feature will add semantic search — finding memories by meaning rather than exact terms, using local embedding models to keep all data on-device. Track progress in the GitHub issues.

---

## Team Memories

For shared team memories, the simplest approach is to point `DB_PATH` in `mem.py` to a shared network path accessible by all team members. Because SQLite supports WAL mode concurrent access, multiple readers and a single writer can coexist safely over a network share.

For higher-throughput team scenarios, swap the `mem.py` storage backend for a lightweight PostgreSQL or MySQL instance while keeping the same JSON interface between SKILL.md and mem.py unchanged.
