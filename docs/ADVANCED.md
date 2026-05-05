# Advanced Configuration

## Semantic Search with pgvector

Full-text search finds memories containing the words you search for.
Semantic search finds memories that MEAN what you're looking for,
even if they use different words.

To enable:
1. Go to Supabase → Database → Extensions → enable `vector`
2. Run `scripts/schema_pgvector.sql` in SQL Editor
3. Generate embeddings when storing memories (requires OpenAI or similar API)

## Using Supabase MCP (Claude Sandbox)

When Claude is running in the sandbox environment, it can connect to
Supabase directly via MCP without needing the Python helper.

Add to your Supabase MCP configuration:
```json
{
  "type": "url",
  "url": "https://mcp.supabase.com/mcp",
  "name": "supabase-mcp"
}
```

Then Claude can use `execute_sql` directly with your project ID.

## Team Memories (Shared Database)

For teams sharing memories:
1. Create a shared Supabase project
2. Enable RLS with user-based policies
3. Add a `user_id` column to `claude_memories`
4. Each team member uses their own auth token

Use Supabase's built-in RLS policy editor to configure per-user access.

## Auto-Checkpoint (Coming in v1.3)

Future versions will support automatic checkpointing every N messages.
Track progress in the GitHub issues tab.

## Export to Obsidian / Markdown

Export all memories to Markdown files:
```bash
python3 scripts/mem.py list --json | python3 scripts/export_obsidian.py
```
(Export script coming in v1.3)
