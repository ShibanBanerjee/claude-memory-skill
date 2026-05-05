# Changelog

## [1.2.0] — 2026-05-05

### Added
- `instructions` field — captures user-defined preferences and directives alongside decisions
- `updated_at` column with automatic trigger — tracks when a memory entry was last revised
- `/mem update` — merges new content into an existing memory rather than creating a duplicate
- Supabase MCP integration as the primary write path from the Claude sandbox environment
- `references/QUALITY_RUBRIC.md` — explicit standards for what makes a useful memory entry
- Full test suite: `tests/test_connection.py`, `test_storage.py`, `test_search.py`
- Platform setup scripts: `scripts/setup.sh` and `scripts/setup.ps1`
- `scripts/verify.py` — end-to-end installation checker

### Changed
- Storage target raised to 1,500–4,000 words per summary — detail is preserved over brevity
- `/mem` now checks existing memories for the project before writing, enabling intelligent updates
- `key_decisions` entries now require the reasoning and any rejected alternatives, not just the outcome
- `memory_cards` view updated to include `last_updated` and `instruction_count`

### Fixed
- PostgreSQL generated column syntax incompatibility — replaced with trigger-based `search_vector`
- Auth header logic updated to handle both legacy anon JWT and new publishable key formats

## [1.0.0] — 2026-04-20

Initial release.

- `/mem` and `/context` slash commands
- Supabase PostgreSQL storage with full-text search
- `scripts/mem.py` CLI helper
- `scripts/schema.sql` with GIN indexes and `memory_cards` view
- `SKILL.md` with YAML frontmatter for Claude Skills standard compatibility
