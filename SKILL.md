---
name: persistent-memory
description: Gives Claude persistent, searchable memory across conversations stored locally on your machine. Use /mem to save conversation context, /context to restore it, /mem list to see all memories.
---

# Claude Memory Skill — /mem and /context

## What This Skill Does

Gives Claude persistent, searchable memory across conversations. All data is stored in a local SQLite database on your machine — no accounts, no cloud services.

Works on **Mac, Linux, and Windows**.

**Trigger words:**
- `/mem` `/mem [title]` `/memory` `/remember this` — save conversation to memory
- `/mem list` `/memories` — list all saved memories
- `/context [query]` `/ctx [query]` `/recall [query]` — retrieve and restore memory

---

## Step 0: Detect Connection Mode — Run at the Start of Every Session

Before anything else, detect which mode to use. Run this exact block:

```bash
# Try direct mode first (Mac/Linux with mem.py at ~/mem.py)
if python3 ~/mem.py setup 2>/dev/null | grep -q "ready\|Memories"; then
  echo "MODE=direct"
else
  # Try HTTP server mode (Windows, or Mac/Linux running mem_server.py)
  MEM_HOST=""
  for host in localhost host.docker.internal 172.17.0.1 172.18.0.1; do
    if curl -sf --max-time 2 "http://$host:7823/health" 2>/dev/null | grep -q "ok"; then
      MEM_HOST="$host"
      echo "MODE=http HOST=$host"
      break
    fi
  done
  if [ -z "$MEM_HOST" ]; then
    echo "MODE=none"
  fi
fi
```

**If MODE=direct** → use all `python3 ~/mem.py ...` commands below.
**If MODE=http** → use all `curl http://$MEM_HOST:7823/...` commands below.
**If MODE=none** → mem.py is not installed. Tell the user:

> `mem.py` or `mem_server.py` is not installed on your machine yet. Open your own terminal (not this chat) and run:
>
> **Mac/Linux:**
> ```bash
> curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py
> python3 ~/mem.py setup
> ```
>
> **Windows PowerShell:**
> ```powershell
> Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"
> Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden
> ```
> Then try your command again.

---

## /mem Command — Full Execution Protocol

### Step 1: Check for existing memory — UPSERT LOGIC

Derive a `project` slug from the conversation topic (lowercase, hyphen-separated, e.g. `backend-rewrite`, `devam-strategy`, `personal`).

**Direct mode:**
```bash
python3 ~/mem.py check --project "project-slug"
```

**HTTP mode:**
```bash
curl -sf "http://$MEM_HOST:7823/check?project=project-slug"
```

Response when a memory exists:
```json
{"exists": true, "id": "uuid", "title": "...", "created_at": "...", "updated_at": "..."}
```

Response when none exists:
```json
{"exists": false}
```

**If exists → UPDATE path (Step 4 update). If not → INSERT path (Step 4 store).**
The updated memory must include everything from the previous version PLUS everything new — nothing is lost.

---

### Step 2: Generate the detailed memory — NO LOSSY COMPRESSION

Read the entire conversation from beginning to end. Do not skim. Your goal is LOSSLESS CAPTURE — not token minimisation.

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

### Step 4: Store or Update

**STORE — Direct mode (new memory):**
```bash
python3 ~/mem.py store << 'MEMORY_JSON'
{ ...json from Step 3... }
MEMORY_JSON
```

**STORE — HTTP mode (new memory):**
```bash
curl -sf -X POST "http://$MEM_HOST:7823/store" \
  -H "Content-Type: application/json" \
  -d '{ ...json from Step 3... }'
```

**UPDATE — Direct mode (existing memory, use ID from Step 1):**
```bash
python3 ~/mem.py update --id "uuid-from-step-1" << 'MEMORY_JSON'
{ ...json from Step 3... }
MEMORY_JSON
```

**UPDATE — HTTP mode (existing memory):**
```bash
curl -sf -X POST "http://$MEM_HOST:7823/update?id=uuid-from-step-1" \
  -H "Content-Type: application/json" \
  -d '{ ...json from Step 3... }'
```

Expected responses:
```json
{"status": "stored", "id": "new-uuid", "title": "...", "created_at": "..."}
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
Start a new conversation and type /context [project] to resume with a fresh context window.
```

---

## /context Command — Retrieval Protocol

### Step 1: Search

**Direct mode:**
```bash
python3 ~/mem.py search --query "query terms here" --limit 5
```

**HTTP mode:**
```bash
curl -sf "http://$MEM_HOST:7823/search?query=query+terms+here&limit=5"
```

If no results, try broader terms. If still nothing:

**Direct mode:**
```bash
python3 ~/mem.py list --limit 20
```

**HTTP mode:**
```bash
curl -sf "http://$MEM_HOST:7823/list?limit=20"
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

**Direct mode:**
```bash
python3 ~/mem.py list --limit 20
```

**HTTP mode:**
```bash
curl -sf "http://$MEM_HOST:7823/list?limit=20"
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
| `MODE=none` — neither direct nor HTTP works | mem.py (Mac/Linux) or mem_server.py (Windows) is not installed on the user's machine. Provide install commands from Step 0. Remind them: Claude cannot install this — they must run the commands themselves in their own terminal. **Mac/Linux:** `curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py && python3 ~/mem.py setup` **Windows:** `Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py" -OutFile "$env:USERPROFILE\mem_server.py"` then `Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden` |
| `Connection refused` on curl | mem_server.py is not running. User must start it: Windows: `Start-Process python -ArgumentList "$env:USERPROFILE\mem_server.py" -WindowStyle Hidden` — Mac/Linux: `python3 ~/mem_server.py &` |
| `No search results` | Try simpler terms, then `/mem list` to browse all memories |
| `ERROR: Invalid JSON` | Rebuild the JSON object carefully — check for unescaped quotes or special characters |
