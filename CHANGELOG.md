# Changelog

## [2.2.0] — 2026-05-06

### Changed
- Storage backend reverted to Supabase PostgreSQL — more reliable across all platforms, especially Windows and Claude Desktop
- `mem.py` now uses Supabase PostgREST REST API via the `requests` library
- `SKILL.md` updated with dual connection mode: Supabase MCP (`execute_sql`) as primary, `mem.py` REST as fallback
- `schema.sql` updated to PostgreSQL DDL with UUID primary key, TIMESTAMPTZ, JSONB, TEXT[], and a TSVECTOR trigger for full-text search
- `INSTALL.md` updated with Supabase MCP and mem.py REST setup instructions

### Removed
- `mem_server.py` — local HTTP server (no longer needed; Supabase handles cross-platform storage)
- `scripts/start_mem_server.sh` / `scripts/start_mem_server.ps1` — server startup scripts
- `docs/WINDOWS.md` — Windows-specific server documentation
- SQLite schema and FTS5 trigger setup

---

## [2.1.0] — 2026-05-06

### Added
- `mem_server.py` — lightweight local HTTP server enabling Windows Claude Desktop support
- `scripts/start_mem_server.ps1` / `scripts/start_mem_server.sh` — startup scripts for Windows and Mac/Linux
- `docs/WINDOWS.md` — complete Windows setup and troubleshooting guide
- `docs/API_REFERENCE.md` — full CLI and HTTP API documentation

### Changed
- `SKILL.md` restructured with Step 0 auto-detection block and dual-mode (Direct / HTTP) commands

---

## [2.0.0] — 2026-05-06

### Changed
- Storage backend moved from Supabase PostgreSQL to local SQLite — zero setup, no accounts required
- `mem.py` rewritten to use Python's built-in `sqlite3` module — no external dependencies
- Database created automatically at `~/.claude_memory.db` on first run

### Added
- `mem.py check --project` — upsert pre-flight returning existing memory ID
- `mem.py update --id` — dedicated update path for existing memories
- WAL mode, FTS5 full-text search, and LIKE fallback search

### Removed
- Supabase MCP integration
- `~/.claude_memory_config.json` credentials file
- `requests` dependency

---

## [1.2.0] — 2026-05-05

### Added
- `instructions` field — captures user-defined preferences and directives
- `updated_at` column with automatic trigger
- `/mem update` — merges new content into an existing memory
- `references/QUALITY_RUBRIC.md` — quality standards for memory entries
- Full test suite: `test_connection.py`, `test_storage.py`, `test_search.py`
- Platform setup scripts: `scripts/setup.sh` and `scripts/setup.ps1`
- `scripts/verify.py` — end-to-end installation checker

### Changed
- Storage target raised to 1,500–4,000 words per summary
- `/mem` now checks existing memories before writing, enabling intelligent updates
- `key_decisions` entries now require reasoning and rejected alternatives

### Fixed
- Auth header logic updated to handle both legacy anon JWT and publishable key formats

---

## [1.0.0] — 2026-04-20

Initial release.
- `/mem` and `/context` slash commands
- Supabase PostgreSQL storage with full-text search
- `scripts/mem.py` CLI helper
- `SKILL.md` with YAML frontmatter for Claude Skills standard compatibility
