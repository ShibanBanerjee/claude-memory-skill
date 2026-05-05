# Command Reference

## /mem — Save Conversation to Memory

### Basic usage
```
/mem
```
Saves the current conversation with an auto-generated title.

### With title
```
/mem Product Strategy Session
/mem My Project Brainstorm May 2026
/mem Auth Service — Design Complete
```
Saves with the provided title. Be specific — the title is your primary way to find this memory later.

### List all memories
```
/mem list
/memories
```
Shows all saved memories in reverse chronological order with ID, title, project, tags, decision count, and question count.

---

## /context — Retrieve and Restore Memory

### Search by topic
```
/context my-project
/context product strategy
/context VC preparation
```
Full-text search across all memory fields — title, project, summary, and tags.

### Search with multiple terms
```
/context my-project VC preparation
/context auth service decisions
/context constellation architecture habit loop
```
More specific queries return more targeted results.

### Project-specific
```
/context project:my-project
/context project:backend
```
Returns all memories for a specific project, newest first.

### Retrieve by ID
```
/context id:e1ccaea5-7cb2-4893-871b-cc83846e5c3e
```
Retrieves a specific memory by its UUID. Use when you know exactly which memory you want.

---

## /recall — Alias for /context

```
/recall my-project brainstorm
/recall product decisions
```
Identical to `/context`. Use whichever feels more natural.

---

## /ctx — Short alias for /context

```
/ctx my-project
/ctx auth
```

---

## Loading Multiple Memories

Run `/context` multiple times in the same session to build up a composite context:

```
/context project strategy
/context my-project VC preparation
/context auth design
```

Claude will load all three memories and synthesise them into a single working context. It will note the date of each, flag any contradictions, and operate with the full accumulated knowledge of all three sessions.

---

## mem.py CLI — Local Machine Usage

The `mem.py` script provides the same capabilities from your local terminal.

### Setup test
```bash
python3 ~/mem.py setup
```

### Search
```bash
python3 ~/mem.py search --query "architecture decision" --limit 5
python3 ~/mem.py search --query "database" --project "my-project" --limit 3
```

### List
```bash
python3 ~/mem.py list --limit 20
python3 ~/mem.py list --project "my-project"
```

### Get by ID
```bash
python3 ~/mem.py get --id "e1ccaea5-7cb2-4893-871b-cc83846e5c3e"
```

### Store (advanced — normally Claude does this for you)
```bash
cat my_memory.json | python3 ~/mem.py store --title "My Memory" --project "MyProject"
```

---

## Tips

**Checkpoint regularly in long sessions**
In a 2-hour brainstorm, run `/mem` every 30–45 minutes. Each checkpoint captures the work so far. If the session ends unexpectedly, nothing is lost.

**Be specific with titles**
`/mem` → "Conversation 2026-05-05" (hard to find later)  
`/mem My Project VC prep — monetisation model and objection handling` → immediately findable

**Use `/context` before starting any continuation session**
Don't try to paste context manually. Just type `/context [project]` and let Claude restore everything.

**Search is flexible**
`/context auth` finds memories tagged "auth" OR containing "auth" in the title or summary. You don't need to be exact.

**Check what's stored before a big session**
`/mem list` at the start of a session gives you a map of what's already in memory before you dive in.
