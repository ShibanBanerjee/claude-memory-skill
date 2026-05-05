# Claude Memory Skill — /mem and /context

## What This Skill Does
Gives Claude persistent, searchable memory across conversations using a Supabase PostgreSQL database.

**Trigger words:**
- `/mem` `/mem [title]` `/memory` `/remember this` — save conversation to memory
- `/mem list` `/memories` — list all saved memories
- `/context [query]` `/ctx [query]` `/recall [query]` — retrieve and restore memory

---

## Configuration
- **Supabase Project ID:** set in `~/.claude_memory_config.json`
- **mem.py location:** `~/mem.py`
- **Config file:** `~/.claude_memory_config.json`

---

## /mem Command — Full Execution Protocol

### Step 1: Check existing memories first
Before generating a new memory, always check what is already stored:

```sql
SELECT id, title, project, created_at, jsonb_array_length(key_decisions) as decisions
FROM claude_memories ORDER BY created_at DESC LIMIT 10;
```

This prevents duplication and tells you if an update is better than a new entry.

### Step 2: Generate the detailed memory — NO LOSSY COMPRESSION

Read the entire conversation from beginning to end. Do not skim. The database has no meaningful size limit. Your goal is LOSSLESS CAPTURE — not token minimisation.

Target summary length: **1,500 to 4,000 words.**

The summary must contain ALL of the following:
1. Project/topic overview from scratch — what this is, why it matters
2. All key concepts defined precisely — especially any coined terms or frameworks
3. All decisions made WITH their reasoning — not just what, but why
4. All ideas REJECTED and why — future Claude must not re-propose rejected ideas
5. All specific numbers — revenue figures, user targets, market sizes, dates, percentages
6. All frameworks or methodologies applied and to what
7. Current status — what is complete, what is next, where things stand exactly
8. Any standing instructions given by the user during the conversation
9. Tone/style preferences if specified
10. All documents or artifacts produced — their titles, contents, and purpose

**Forbidden patterns:**
- "we discussed X" → write what was DECIDED about X
- "various options explored" → list the actual options and what happened to each
- Omitting specific numbers → always include them
- Omitting rejections → rejected ideas are as critical as accepted ones

### Step 3: Structure the JSON

```json
{
  "title": "Specific descriptive title (max 100 chars)",
  "project": "Project or domain name e.g. backend-rewrite, my-startup, personal",
  "conversation_url": "URL if known",
  "tags": ["5 to 10 specific searchable tags"],
  "summary": "1500-4000 word detailed narrative — see Step 2",
  "key_decisions": [
    "What was decided — Why it was decided / what problem it solves / what was rejected instead"
  ],
  "open_questions": [
    "Specific actionable question with enough context to understand without reading the full summary"
  ],
  "entities": {
    "people": ["names and roles"],
    "products": ["product names"],
    "companies": ["company names"],
    "concepts": ["key concepts, frameworks, methodologies"],
    "documents": ["document names produced or referenced"]
  },
  "token_count_est": 0
}
```

### Step 4: Store via Supabase MCP (primary path)

```sql
INSERT INTO claude_memories (
  title, project, conversation_url, summary, tags,
  key_decisions, open_questions, entities, token_count_est
) VALUES (
  'title here',
  'project here',
  'url or empty',
  'full summary here',
  ARRAY['tag1','tag2','tag3'],
  '["decision 1","decision 2"]'::jsonb,
  '["question 1","question 2"]'::jsonb,
  '{"people":[],"products":[]}'::jsonb,
  2000
) RETURNING id, title, created_at;
```

Fallback (user machine): `cat memory.json | python3 ~/mem.py store --title "..." --project "..."`

### Step 5: Confirm to user

```
✅ Memory saved.
Title: [title]
Project: [project]
Memory ID: [uuid]
Summary: ~[N] words
Decisions captured: [N]
Open questions: [N]
Tags: [tags]

Restore in any future session with: /context [topic]
```

---

## /context Command — Retrieval Protocol

### Step 1: Search

Primary (MCP SQL):
```sql
SELECT id, title, project, tags, summary, key_decisions, open_questions, entities, conversation_url, created_at
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'query terms here')
ORDER BY created_at DESC LIMIT 5;
```

Fallback: `python3 ~/mem.py search --query "query" --limit 5`

### Step 2: Present findings
Show title, project, date, decision count, question count, first 200 chars of summary.

### Step 3: Load into working context
- Treat summary as fully known background
- Treat key_decisions as settled — do not re-open unless user asks
- Treat open_questions as the current agenda
- Say clearly: "I have loaded the [project] context. [One sentence orientation]. Where would you like to resume?"

### Step 4: Multi-memory
If multiple memories loaded: note dates (recent wins conflicts), synthesise, flag contradictions.

---

## /mem list

```sql
SELECT id, created_at::DATE as date, title, project, tags,
  jsonb_array_length(key_decisions) as decisions,
  jsonb_array_length(open_questions) as questions
FROM claude_memories ORDER BY created_at DESC LIMIT 20;
```

---

## Quality Checklist — Before Storing

A good memory lets future Claude:
- [ ] Know what the project is without any other context
- [ ] Know what was decided AND why
- [ ] Know what was rejected AND why
- [ ] Know all specific numbers used
- [ ] Know what documents/artifacts exist and what they contain
- [ ] Know the immediate next steps
- [ ] Resume work without asking clarifying questions

---

## Error Handling

| Error | Action |
|---|---|
| Supabase MCP unavailable | Fall back to mem.py |
| Connection 403 | Use legacy anon key (eyJ...), not publishable key (sb_...) |
| No search results | Try tag match, then project match, then list all |
| Memory very large | Split into Part 1/2 entries |
