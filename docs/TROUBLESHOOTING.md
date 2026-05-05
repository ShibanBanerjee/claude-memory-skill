# Troubleshooting

## "No such file or directory: ~/mem.py"

`mem.py` hasn't been installed yet. Run:

```bash
# Mac / Linux
cp scripts/mem.py ~/mem.py

# Windows PowerShell
Copy-Item scripts\mem.py "$env:USERPROFILE\mem.py"
```

## "python3: command not found"

Python 3 is not installed or not on your PATH.

- **Mac / Linux:** Install from [python.org](https://python.org), or via your package manager (`brew install python3`, `apt install python3`)
- **Windows:** Download from [python.org](https://python.org) — check "Add Python to PATH" during installation. Use `python` instead of `python3` in PowerShell if needed.

## "/mem doesn't trigger the skill"

Confirm SKILL.md is installed in the correct location:

- **Claude Code:** `~/.claude/skills/claude-memory/SKILL.md`
- **Claude.ai:** uploaded via Settings → Skills

## "Search returns no results"

- Try simpler, broader search terms — FTS5 does exact token matching
- Run `/mem list` to confirm memories have been saved
- Use `/context id:[uuid]` to retrieve by the exact ID returned at save time

## "ERROR: Invalid JSON"

The JSON object piped to `mem.py store` is malformed. This is rare. If it occurs:

1. Run `/mem` again — Claude regenerates the JSON from scratch
2. If the error persists, run `python3 ~/mem.py setup` to confirm the database is accessible

## "OperationalError: no such module: fts5"

Your Python's bundled SQLite was compiled without FTS5. This is uncommon on modern systems.

- **Mac:** Use the Python from [python.org](https://python.org) rather than the system Python
- **Linux:** Install `libsqlite3-dev` and recompile Python, or use a package manager version that includes FTS5
- Verify with: `python3 -c "import sqlite3; db=sqlite3.connect(':memory:'); db.execute('CREATE VIRTUAL TABLE t USING fts5(x)')"`

## Database appears empty after reinstalling mem.py

The database at `~/.claude_memory.db` persists across skill and `mem.py` reinstalls. If memories are missing, verify the path:

```bash
python3 ~/mem.py setup
```

The output shows the exact database path being used.

## "token_count_est seems wrong"

`token_count_est` is an approximate word count of the summary, not an exact token count. It is used as a rough reference only.
