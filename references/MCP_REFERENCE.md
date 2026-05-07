# Supabase MCP SQL Quick Reference

All SQL commands Claude uses when the Supabase MCP (`execute_sql`) tool is available.

---

## Check if project memory exists

```sql
SELECT id, title, created_at, updated_at
FROM claude_memories
WHERE project = 'project-slug'
ORDER BY updated_at DESC
LIMIT 1;
```

Returns a row (exists) or empty result (not found).

---

## Store a new memory

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
  '["Open question 1", "Open question 2"]'::jsonb,
  '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  ARRAY['tag1', 'tag2', 'tag3'],
  450
)
RETURNING id, title, created_at;
```

---

## Update an existing memory

```sql
UPDATE claude_memories SET
  updated_at       = NOW(),
  title            = 'Updated title',
  project          = 'project-slug',
  conversation_url = '',
  summary          = 'Full updated summary...',
  key_decisions    = '["Decision 1", "Decision 2"]'::jsonb,
  open_questions   = '["Open question 1"]'::jsonb,
  entities         = '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  tags             = ARRAY['tag1', 'tag2'],
  token_count_est  = 450
WHERE id = 'uuid-from-check'
RETURNING id, title, updated_at;
```

---

## Search by full-text

```sql
SELECT id, title, project, created_at, updated_at, tags, token_count_est,
       LEFT(summary, 300) AS summary_preview
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'search terms here')
ORDER BY updated_at DESC
LIMIT 5;
```

---

## List all memories

```sql
SELECT id, title, project, created_at, updated_at, tags, token_count_est
FROM claude_memories
ORDER BY updated_at DESC
LIMIT 20;
```

---

## Get full record by ID

```sql
SELECT * FROM claude_memories WHERE id = 'uuid-here';
```

---

## Search by tag

```sql
SELECT id, title, project, updated_at
FROM claude_memories
WHERE 'tag-name' = ANY(tags)
ORDER BY updated_at DESC;
```

---

## Count memories by project

```sql
SELECT project, COUNT(*) AS count
FROM claude_memories
GROUP BY project
ORDER BY count DESC;
```
