# Troubleshooting

## Installation Issues

### `execute_sql` fails with "relation does not exist"
The `claude_memories` table hasn't been created yet. Open your Supabase project → SQL Editor → New Query, paste `schema.sql`, and run it.

### `ERROR: Config file not found`
`~/.claude_memory_config.json` doesn't exist. Create it:
```json
{
  "supabase_url": "https://your-project.supabase.co",
  "supabase_anon_key": "your-anon-key"
}
```
Your URL and anon key are at: Supabase Dashboard → Project Settings → API.

### `ERROR: requests library not found`
Install the requests library:
```bash
pip install requests
```

### `python3: command not found`
Install Python 3.8+ from [python.org](https://python.org). On Windows, use `python` instead of `python3` and check "Add Python to PATH" during installation.

### Skills not appearing in Claude
- Confirm you have a Pro, Max, Team, or Enterprise plan — the free tier has no Skills access.
- Re-upload `SKILL.md` via Settings → Skills → Remove existing → Add Custom Skill.
- In Claude Desktop, fully quit and relaunch after uploading a new skill.

---

## Runtime Issues

### `MODE=none` — Neither MCP nor mem.py works
1. **MCP path**: Confirm the Supabase MCP integration is configured in Claude's settings.
2. **mem.py path**: Confirm `~/mem.py` exists and `~/.claude_memory_config.json` is present with valid credentials. Run `python3 ~/mem.py setup` in your terminal to test the connection.

### `/mem list` shows empty even though memories were saved
Run `python3 ~/mem.py setup` in your local terminal (not inside Claude). If it prints `Memories stored: 0`, the connection is working but no records exist — or you're pointing at a different Supabase project than you saved to.

Check that `supabase_url` in your config matches the project where you ran `schema.sql`.

### `/context` finds nothing when I search
Try simpler, shorter search terms — single keywords rather than phrases. Then use `/mem list` to browse all memories and confirm they're there. If the search_vector column is empty, rebuild it:
```sql
UPDATE claude_memories SET updated_at = updated_at;
```

### Supabase project is paused
Free-tier Supabase projects pause after one week of inactivity. Go to your Supabase dashboard and resume the project. It takes about 30 seconds to wake up.

### `ERROR: Supabase API error (401)`
Your anon key is incorrect or expired. Get the current key from: Supabase Dashboard → Project Settings → API → `anon` `public` key. Update `~/.claude_memory_config.json`.

### `ERROR: Supabase API error (403)`
Row Level Security is blocking writes. Either disable RLS (`ALTER TABLE claude_memories DISABLE ROW LEVEL SECURITY;`) or add an appropriate policy. See `docs/ADVANCED.md`.

### `ERROR: Invalid JSON`
Usually caused by unescaped special characters in a long summary. Claude will rebuild the JSON and retry automatically. If it persists, try saving a shorter portion of the conversation.

---

## Data Issues

### I want to view all memories directly
Use the Supabase Dashboard → Table Editor → `claude_memories`. Or in the SQL Editor:
```sql
SELECT id, title, project, updated_at FROM claude_memories ORDER BY updated_at DESC;
```

### I want to delete a specific memory
```sql
DELETE FROM claude_memories WHERE id = 'uuid-here';
```

### I want to start completely fresh
```sql
TRUNCATE claude_memories;
```
This removes all memories permanently. There is no undo.

### I want to export all memories
```bash
python3 ~/mem.py list --limit 10000 > memories_export.json
```
Or use Supabase Dashboard → Table Editor → Export to CSV.
