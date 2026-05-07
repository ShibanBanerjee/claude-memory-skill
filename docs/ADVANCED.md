# Advanced Configuration

## Supabase Project Settings

By default, `mem.py` reads credentials from `~/.claude_memory_config.json`. To use a different path, set the `CLAUDE_MEMORY_CONFIG` environment variable (requires editing `mem.py` — the variable is not checked by default, but the `CONFIG_PATH` constant at the top of the file can be pointed anywhere).

---

## Row Level Security

The default schema disables Row Level Security (RLS) so the anon key can read and write without restrictions. For production use or multi-user setups, enable RLS and add appropriate policies:

```sql
-- Enable RLS
ALTER TABLE claude_memories ENABLE ROW LEVEL SECURITY;

-- Allow any authenticated user to read all memories
CREATE POLICY "read_all" ON claude_memories
  FOR SELECT USING (true);

-- Allow insert and update only with a valid service role key
CREATE POLICY "write_service" ON claude_memories
  FOR ALL USING (auth.role() = 'service_role');
```

---

## Exporting Memories

Export all memories as JSON using mem.py:

```bash
python3 ~/mem.py list --limit 10000 > memories_export.json
```

Or query Supabase directly in the SQL Editor:

```sql
SELECT * FROM claude_memories ORDER BY updated_at DESC;
```

Use the Supabase Dashboard → Table Editor → Export CSV for spreadsheet-friendly output.

---

## Querying Directly in Supabase

The Supabase SQL Editor gives you direct access to all stored memories:

```sql
-- Count all memories
SELECT COUNT(*) FROM claude_memories;

-- List memories by project
SELECT id, title, created_at FROM claude_memories WHERE project = 'my-project';

-- Full-text search
SELECT title, project
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'architecture database');

-- Tag search (exact match on any tag in array)
SELECT title, project
FROM claude_memories
WHERE 'auth' = ANY(tags);

-- Most recent memories
SELECT id, title, project, updated_at
FROM claude_memories
ORDER BY updated_at DESC
LIMIT 10;
```

---

## Rebuilding the Search Index

If the `search_vector` column gets out of sync (possible after a bulk data import that bypassed the trigger), rebuild it:

```sql
UPDATE claude_memories SET updated_at = updated_at;
```

This touches every row and re-fires the `BEFORE UPDATE` trigger, which repopulates `search_vector` for each record.

---

## pgvector Semantic Search (Roadmap)

The current search finds memories by keyword match against the `search_vector` TSVECTOR column. A planned future feature will add semantic search using pgvector — finding memories by meaning rather than exact terms. See `scripts/schema_pgvector.sql` for the draft schema.

---

## Team Memories

For shared team memories, point every team member's `~/.claude_memory_config.json` at the same Supabase project. All team members write to and read from the shared `claude_memories` table. Use the `project` field to namespace memories by team, initiative, or individual if needed.

For stricter isolation, enable RLS with per-user policies, or use separate Supabase projects per team.

---

## Backing Up Your Memories

Supabase automatically backs up your database on paid plans. For manual backups, export via the SQL Editor or use the Supabase CLI:

```bash
supabase db dump --linked > claude_memories_backup.sql
```

To restore:
```bash
supabase db push --linked < claude_memories_backup.sql
```

Or restore individual records by re-running the INSERT statements from the export.
