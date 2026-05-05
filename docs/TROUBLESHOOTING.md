# Troubleshooting

## "Config file not found"
Create `~/.claude_memory_config.json` with your Supabase URL and anon key.
See docs/SETUP.md for exact commands per OS.

## "Connection failed: 403 — Host not in allowlist"
This happens when using the new publishable key (`sb_publishable_...`) from
a script. Use the **legacy anon key** instead:
- Go to Supabase → Settings → API Keys → "Legacy anon, service_role API keys" tab
- Copy the key starting with `eyJ...`

## "Connection failed: 404"
The `claude_memories` table doesn't exist yet.
Run `scripts/schema.sql` in your Supabase SQL Editor.

## "Connection failed: 401 Unauthorized"
Your API key is incorrect or expired.
Double-check it in Supabase → Settings → API Keys.

## "/mem doesn't trigger the skill"
Make sure SKILL.md is installed in the correct location:
- Claude Code: `~/.claude/skills/claude-memory/SKILL.md`
- Claude.ai: uploaded via Settings → Skills

## "Search returns no results"
- Try simpler, broader search terms
- Use `/mem list` to see all stored memories
- Check that the memory was saved (confirm with the ID returned at save time)

## Memory saves but search can't find it
The full-text search trigger may not have fired. Run this in Supabase SQL Editor:
```sql
UPDATE claude_memories SET title = title WHERE id = 'your-memory-id';
```
This forces the search vector to rebuild.

## "Token count seems wrong"
`token_count_est` is the word count of the summary, not actual token count.
It's an approximation used for reference only.
