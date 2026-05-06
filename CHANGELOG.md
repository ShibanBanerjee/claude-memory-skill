# Changelog

## [2.1.0] — 2026-05-06

### Added
- `mem_server.py` — lightweight local HTTP server enabling Windows Claude Desktop support. Exposes all memory operations as JSON endpoints on `localhost:7823`. Pure Python stdlib, zero dependencies.
- `scripts/start_mem_server.ps1` — Windows PowerShell startup script. Downloads `mem_server.py` if missing, starts it as a hidden background process, prints Task Scheduler commands for auto-start on login.
- `scripts/start_mem_server.sh` — Mac/Linux startup script with launchd (Mac) and systemd (Linux) auto-start instructions.
- `SKILL.md` now includes Step 0: auto-detection block that probes for direct python3 mode (Mac/Linux) and HTTP server mode (Windows) at the start of every session. Platform-agnostic — same SKILL.md works everywhere.
- HTTP API endpoints: `GET /health`, `/setup`, `/check`, `/list`, `/search`, `/get` · `POST /store`, `/update`
- `docs/WINDOWS.md` — complete Windows setup guide explaining the container architecture and server approach.
- `docs/API_REFERENCE.md` updated with full HTTP API documentation.

### Changed
- `SKILL.md` restructured: every command now has a Direct mode (Mac/Linux) and HTTP mode (Windows) variant.
- `README.md` updated with Windows Quick Start section and architecture explanation.
- `INSTALL.md` updated with correct file paths (`mem.py` at repo root, not `scripts/mem.py`) and Windows server install steps.
- Error handling in `SKILL.md` now provides correct, platform-specific install commands — no more placeholder URLs.

### Fixed
- `INSTALL.md` previously referenced `scripts/mem.py` (wrong path — `mem.py` is at repo root).
- Error recovery instructions in `SKILL.md` previously showed placeholder `your-repo` URL.

---

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
