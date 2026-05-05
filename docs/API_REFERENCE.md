# API Reference

## Database Schema

### claude_memories

| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key, auto-generated |
| created_at | TIMESTAMPTZ | When memory was first saved |
| updated_at | TIMESTAMPTZ | When memory was last updated |
| conversation_id | TEXT | Claude conversation ID if known |
| conversation_url | TEXT | URL to the original conversation |
| title | TEXT (required) | Descriptive title |
| project | TEXT | Project or domain name for filtering |
| summary | TEXT (required) | Full detailed narrative (1,500-4,000 words) |
| key_decisions | JSONB | Array of decision strings with reasoning |
| open_questions | JSONB | Array of specific actionable questions |
| instructions | JSONB | Array of user preference/directive strings |
| entities | JSONB | Object: {people, products, companies, ...} |
| tags | TEXT[] | Searchable keyword array |
| token_count_est | INTEGER | Approximate word count of summary |
| search_vector | TSVECTOR | Auto-maintained full-text search index |

### memory_cards (view)
Compact view for listing. Columns: id, date, last_updated, title, project,
tags, preview (300 chars), decision_count, question_count, instruction_count,
token_count_est, conversation_url.

## REST API (via Supabase)

Base URL: `https://YOUR_PROJECT.supabase.co/rest/v1`

Headers required:
```
Authorization: Bearer YOUR_ANON_KEY
apikey: YOUR_ANON_KEY
Content-Type: application/json
```

### List memories
```
GET /claude_memories?select=*&order=created_at.desc&limit=20
```

### Search
```
GET /claude_memories?search_vector=fts.query+terms&order=created_at.desc
```

### Get by ID
```
GET /claude_memories?id=eq.UUID&select=*
```

### Insert
```
POST /claude_memories
Body: JSON object with required fields title and summary
```

### Update
```
PATCH /claude_memories?id=eq.UUID
Body: JSON object with fields to update
```

### Delete
```
DELETE /claude_memories?id=eq.UUID
```
