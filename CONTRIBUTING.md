# Contributing

PRs and issues are welcome.

## Ways to help

- **Bug reports** — use the issue template; include OS, Python version, and the exact error
- **Documentation** — corrections, clearer wording, additional examples
- **New features** — open an issue to discuss before building; see the roadmap in README
- **Semantic search** — high priority; see `scripts/schema_pgvector.sql` for the draft pgvector schema

## Development setup

```bash
git clone https://github.com/ShibanBanerjee/claude-memory-skill
cd claude-memory-skill

# Install dependencies
pip install requests

# Copy mem.py to home directory
cp scripts/mem.py ~/mem.py

# Create credentials file with your Supabase project details
# ~/.claude_memory_config.json: {"supabase_url": "...", "supabase_anon_key": "..."}

# Verify the connection
python3 ~/mem.py setup

# Run the full test suite
python3 tests/run_all_tests.py
```

## Guidelines

- `SKILL.md` must stay under ~6,000 words — Claude loads this in full on activation
- All storage goes through the Supabase PostgREST API or Supabase MCP — keep the interface consistent with the existing schema
- `mem.py` requires `requests` but no other external packages
- New features should include tests in `tests/`
- Python must work on 3.8+
- Update `CHANGELOG.md` under an `[Unreleased]` header

## Submitting a PR

1. Fork the repo and create a branch off `main`
2. Make your changes
3. Run `python3 tests/run_all_tests.py` — all tests must pass
4. Submit the PR with a short description of what changed and why

## Code of conduct

Keep it focused on the work. Disagreements about approach are fine; personal attacks are not.
