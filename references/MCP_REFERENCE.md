# Supabase MCP Reference

The preferred way to interact with the database when running from the
Claude sandbox is via the Supabase MCP tool `execute_sql`.

## Project ID
Your project ID is in the URL when you're in the Supabase dashboard:
`https://supabase.com/dashboard/project/YOUR_PROJECT_ID`

## Common Queries

### Store a memory
```sql
INSERT INTO claude_memories (
  title, project, summary, tags, key_decisions, open_questions,
  instructions, entities, token_count_est
) VALUES (
  'Title here',
  'ProjectName',
  'Full detailed summary here...',
  ARRAY['tag1', 'tag2', 'tag3'],
  '["decision 1 with reasoning", "decision 2 with reasoning"]'::jsonb,
  '["specific open question 1", "specific open question 2"]'::jsonb,
  '["always do X", "never do Y"]'::jsonb,
  '{"people": [], "products": [], "companies": []}'::jsonb,
  2500
) RETURNING id, title, created_at;
```

### Search memories
```sql
SELECT id, title, project, summary, key_decisions, open_questions,
       instructions, tags, created_at
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'search terms here')
ORDER BY created_at DESC LIMIT 5;
```

### List recent
```sql
SELECT id, created_at::DATE, title, project, tags,
  jsonb_array_length(key_decisions) as decisions
FROM claude_memories ORDER BY created_at DESC LIMIT 20;
```

### Update existing
```sql
UPDATE claude_memories
SET summary = '...', key_decisions = '...'::jsonb, open_questions = '...'::jsonb
WHERE id = 'uuid-here'
RETURNING id, updated_at;
```
