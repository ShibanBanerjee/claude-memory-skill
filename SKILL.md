---
name: mem
description: Gives Claude persistent, searchable memory across conversations stored in Supabase PostgreSQL. Use /mem to save conversation context, /context to restore it, /mem list to see all memories.
---

# Claude Memory Skill — /mem and /context

## What This Skill Does

Gives Claude persistent, searchable memory across conversations. All data is stored in your Supabase PostgreSQL database — accessible from every device, every Claude interface, every conversation.

**Trigger words:**
- `/mem` `/mem [title]` `/memory` `/remember this` — save conversation to memory
- `/mem list` `/memories` — list all saved memories
- `/context [query]` `/ctx [query]` `/recall [query]` — retrieve and restore memory

---

## Step 0: Detect Connection Mode — Run at the Start of Every Session

Before anything else, detect which connection mode is available.

**Try MCP mode first** — run this SQL using the `execute_sql` tool (Supabase MCP):
```sql
SELECT COUNT(*) FROM claude_memories;
```

- If it returns a count → **MODE=mcp**. Use the SQL commands in this skill.
- If it errors → **Try REST mode**: run `python3 ~/mem.py setup`
  - If it prints "Claude Memory — Supabase ready" → **MODE=rest**. Use the `python3 ~/mem.py` commands.
  - If it errors → **MODE=none**

**If MODE=none**, tell the user:

> Memory storage is not configured. You have two options:
>
> **Option 1 — Supabase MCP (recommended):**
> Add the Supabase MCP integration to your Claude settings. Once configured, `/mem` works everywhere without any local setup.
>
> **Option 2 — mem.py REST fallback:**
> 1. [Create a free Supabase project](https://supabase.com) and run `schema.sql` in the SQL Editor.
> 2. Create `~/.claude_memory_config.json`:
>    ```json
>    {"supabase_url": "https://xxx.supabase.co", "supabase_anon_key": "your-key"}
>    ```
> 3. `curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py && pip install requests`
>
> See [INSTALL.md](https://github.com/ShibanBanerjee/claude-memory-skill/blob/main/INSTALL.md) for full instructions.

---

## /mem Command — Full Execution Protocol

### Step 1: Check for Existing Memory — Upsert Logic

Derive a `project` slug from the conversation topic (lowercase, hyphenated, e.g. `backend-rewrite`, `devam-strategy`, `personal`).

**MCP mode:**
```sql
SELECT id, title, created_at, updated_at
FROM claude_memories
WHERE project = 'project-slug'
ORDER BY updated_at DESC
LIMIT 1;
```

**REST mode:**
```bash
python3 ~/mem.py check --project "project-slug"
```

Response when a memory exists: `{"exists": true, "id": "uuid", "title": "...", ...}`
Response when none exists: `{"exists": false}`

**If exists → UPDATE path (Step 4 update). If not → INSERT path (Step 4 store).**
The updated memory must include everything from the previous version PLUS everything new — nothing is lost.

---

### Step 2: Generate the Detailed Memory — No Lossy Compression

Read the entire conversation from beginning to end. Do not skim. Goal: LOSSLESS CAPTURE.

**Target summary length: 1,500 to 4,000 words.**

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

---

### Step 3: Structure the JSON

```json
{
  "title": "Specific descriptive title (max 100 chars)",
  "project": "project-slug-matching-step-1",
  "conversation_url": "URL if known, otherwise empty string",
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

---

### Step 4: Store or Update

**STORE — MCP mode (new memory):**
```sql
INSERT INTO claude_memories
  (title, project, conversation_url, summary,
   key_decisions, open_questions, entities, tags, token_count_est)
VALUES (
  'Title here',
  'project-slug',
  '',
  'Full summary text here...',
  '["Decision 1 — reason", "Decision 2 — reason"]'::jsonb,
  '["Open question 1", "Open question 2"]'::jsonb,
  '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  ARRAY['tag1', 'tag2', 'tag3'],
  450
)
RETURNING id, title, created_at;
```

**STORE — REST mode (new memory):**
```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{ ...json from Step 3... }
MEMORY_JSON
```

**UPDATE — MCP mode (existing memory — use ID from Step 1):**
```sql
UPDATE claude_memories SET
  title            = 'Updated title',
  project          = 'project-slug',
  conversation_url = '',
  summary          = 'Full updated summary...',
  key_decisions    = '["Decision 1", "Decision 2"]'::jsonb,
  open_questions   = '["Open question 1"]'::jsonb,
  entities         = '{"people": [], "products": [], "companies": [], "concepts": [], "documents": []}'::jsonb,
  tags             = ARRAY['tag1', 'tag2'],
  token_count_est  = 450
WHERE id = 'uuid-from-step-1'
RETURNING id, title, updated_at;
```
*(The trigger auto-sets `updated_at` and `search_vector` on every write — no need to set them explicitly.)*

**UPDATE — REST mode (existing memory):**
```bash
python3 ~/mem.py update --id "uuid-from-step-1" << 'MEMORY_JSON'
{ ...json from Step 3... }
MEMORY_JSON
```

Expected responses:
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
{"status": "updated", "id": "uuid", "title": "...", "updated_at": "..."}
```

---

### Step 5: Confirm to User

```
✅ Memory saved. [UPDATED existing | NEW entry]
Title: [title]
Project: [project]
Memory ID: [uuid]
Summary: ~[N] words
Decisions captured: [N]
Open questions: [N]
Tags: [tags]

Restore in any future session with: /context [topic]
Start a new conversation and type /context [project] to resume with a fresh context window.
```

---

## /context Command — Retrieval Protocol

### Step 1: Search and Load

**MCP mode** — loads the full record in one query (summary, decisions, questions, entities all included):
```sql
SELECT id, title, project, tags, summary, key_decisions, open_questions,
       instructions, entities, conversation_url, created_at, updated_at
FROM claude_memories
WHERE search_vector @@ plainto_tsquery('english', 'query terms here')
ORDER BY created_at DESC
LIMIT 5;
```

If no results, try broader terms. If still nothing, list all:
```sql
SELECT id, created_at::DATE AS date, title, project, tags,
       jsonb_array_length(key_decisions) AS decisions,
       jsonb_array_length(open_questions) AS questions
FROM claude_memories
ORDER BY created_at DESC
LIMIT 20;
```

**REST mode:**
```bash
python3 ~/mem.py search --query "query terms here" --limit 5
```

If no results:
```bash
python3 ~/mem.py list --limit 20
```

### Step 2: Present Findings
Show title, project, date, decision count, question count, and first 200 chars of summary.

### Step 3: Load into Working Context
- Treat summary as fully known background
- Treat key_decisions as settled — do not re-open unless user asks
- Treat open_questions as the current agenda
- Apply any instructions[] found in the memory
- Say clearly: "I have loaded the [project] context. [One sentence orientation]. Where would you like to resume?"

### Step 4: Multi-Memory
If multiple memories are loaded: note dates (most recent wins on conflicts), synthesise, flag contradictions.

---

## /mem list

**MCP mode:**
```sql
SELECT id, created_at::DATE AS date, title, project, tags,
       jsonb_array_length(key_decisions) AS decisions,
       jsonb_array_length(open_questions) AS questions
FROM claude_memories
ORDER BY created_at DESC
LIMIT 20;
```

**REST mode:**
```bash
python3 ~/mem.py list --limit 20
```

Display results as a readable table: date, title, project, tags, word count.

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
| `execute_sql` fails with "relation does not exist" | Schema not applied. User must run `schema.sql` in their Supabase SQL Editor |
| `execute_sql` tool not available | Fall back to REST mode (mem.py) |
| `ERROR: Config file not found` | User must create `~/.claude_memory_config.json` — see INSTALL.md |
| `ERROR: requests library not found` | User must run `pip install requests` |
| Connection timeout or project paused | Check Supabase dashboard — free-tier projects pause after inactivity |
| `No search results` | Try simpler terms, then `/mem list` to browse all memories |
| `ERROR: Invalid JSON` | Rebuild the JSON carefully — check for unescaped quotes in summary text |
