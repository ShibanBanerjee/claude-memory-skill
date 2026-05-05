---
name: persistent-memory
description: Gives Claude persistent, searchable memory across conversations stored locally on your machine. Use /mem to save conversation context, /context to restore it, /mem list to see all memories.
---

# Claude Memory Skill — /mem and /context

## What This Skill Does
Gives Claude persistent, searchable memory across conversations. All data is stored in a local SQLite database on your machine — no accounts, no cloud services, no configuration required beyond copying two files.

**Trigger words:**
- `/mem` `/mem [title]` `/memory` `/remember this` — save conversation to memory
- `/mem list` `/memories` — list all saved memories
- `/context [query]` `/ctx [query]` `/recall [query]` — retrieve and restore memory

---

## /mem Command — Full Execution Protocol

### Step 1: Check for existing memory — UPSERT LOGIC

Derive a `project` slug from the conversation topic (lowercase, hyphen-separated, e.g. `backend-rewrite`, `my-startup`, `personal`). Then check whether a memory already exists for it:

```bash
python3 ~/mem.py check --project "project-slug"
```

Response when a memory exists:
```json
{"exists": true, "id": "uuid", "title": "...", "created_at": "...", "updated_at": "..."}
```

Response when none exists:
```json
{"exists": false}
```

**If a memory exists for this project:** take the UPDATE path in Step 4. The updated memory must include everything from the previous version PLUS everything new from the current conversation — nothing from the earlier memory should be lost.

**If no memory exists:** take the INSERT path in Step 4.

---

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

### Step 4: Store via mem.py

Pipe the JSON from Step 3 to mem.py using a heredoc to avoid shell quoting issues.

**If creating a new memory** (Step 1 returned `"exists": false`):
```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{"title": "...", "project": "...", "summary": "...", "tags": [...], "key_decisions": [...], "open_questions": [...], "entities": {...}, "token_count_est": 0}
MEMORY_JSON
```

Response:
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
```

**If updating an existing memory** (Step 1 returned `"exists": true` with an ID):
```bash
python3 ~/mem.py update --id "id-from-step-1" << 'MEMORY_JSON'
{"title": "...", "project": "...", "summary": "...", "tags": [...], "key_decisions": [...], "open_questions": [...], "entities": {...}, "token_count_est": 0}
MEMORY_JSON
```

Response:
```json
{"status": "updated", "id": "uuid", "title": "...", "updated_at": "..."}
```

---

### Step 5: Confirm to user

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
To continue with a fresh context window: start a new conversation and type /context [project].
```

---

## /context Command — Retrieval Protocol

### Step 1: Search

```bash
python3 ~/mem.py search --query "query terms here" --limit 5
```

If no results, try broader terms:
```bash
python3 ~/mem.py search --query "broader term" --limit 5
```

If still no results, list all:
```bash
python3 ~/mem.py list --limit 20
```

### Step 2: Present findings
Show title, project, date, decision count, question count, and first 200 chars of summary.

### Step 3: Load into working context
- Treat summary as fully known background
- Treat key_decisions as settled — do not re-open unless user asks
- Treat open_questions as the current agenda
- Say clearly: "I have loaded the [project] context. [One sentence orientation]. Where would you like to resume?"

### Step 4: Multi-memory
If multiple memories are loaded: note dates (most recent wins on conflicts), synthesise, flag contradictions.

---

## /mem list

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
| `python3: command not found` | User needs Python 3.8+. Direct them to python.org |
| `No such file or directory: ~/mem.py` | User hasn't installed mem.py. Run: `cp scripts/mem.py ~/mem.py` |
| `No search results` | Try simpler terms, then `/mem list` to browse all memories |
| `ERROR: Invalid JSON` | Rebuild the JSON object carefully — check for unescaped quotes or special characters |
