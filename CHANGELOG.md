# Changelog

## [2.0.0] — 2026-05-06

### Changed
- Storage backend moved from Supabase PostgreSQL to local SQLite — zero setup, no accounts required
- `mem.py` now uses Python's built-in `sqlite3` module exclusively — no external dependencies
- Database created automatically at `~/.claude_memory.db` on first run
- SKILL.md updated to use `mem.py` CLI for all operations

### Added
- `mem.py check --project` — upsert pre-flight: returns existing memory ID if project has one
- `mem.py update --id` — dedicated update path for existing memories
- WAL mode for safe concurrent access
- FTS5 full-text search with automatic sync triggers on insert, update, and delete
- LIKE fallback search when FTS5 returns no results
- `setup` command initialises the database schema on first run

### Removed
- Supabase MCP integration
- `~/.claude_memory_config.json` credentials file
- `requests` dependency

---

## [1.2.0] — 2026-05-05

### Added
- `instructions` field — captures user-defined preferences and directives alongside decisions
- `updated_at` column with automatic trigger — tracks when a memory entry was last revised
- `/mem update` — merges new content into an existing memory rather than creating a duplicate
- `references/QUALITY_RUBRIC.md` — explicit standards for what makes a useful memory entry
- Full test suite: `tests/test_connection.py`, `test_storage.py`, `test_search.py`
- Platform setup scripts: `scripts/setup.sh` and `scripts/setup.ps1`
- `scripts/verify.py` — end-to-end installation checker

### Changed
- Storage target raised to 1,500–4,000 words per summary
- `/mem` now checks existing memories for the project before writing, enabling intelligent updates
- `key_decisions` entries now require the reasoning and any rejected alternatives, not just the outcome

### Fixed
- Auth header logic updated to handle both legacy anon JWT and new publishable key formats

---

## [1.0.0] — 2026-04-20

Initial release.

- `/mem` and `/context` slash commands
- Supabase PostgreSQL storage with full-text search
- `scripts/mem.py` CLI helper
- `SKILL.md` with YAML frontmatter for Claude Skills standard compatibility
