# Contributing

PRs and issues are welcome.

## Ways to help

- **Bug reports** — use the issue template; include OS, Python version, and the exact error
- **Documentation** — corrections, clearer wording, additional examples
- **New features** — open an issue to discuss before building; see the roadmap in README
- **pgvector integration** — high priority; see `docs/ADVANCED.md` for context

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/claude-memory-skill
cd claude-memory-skill
pip install requests --break-system-packages
cp scripts/mem.py ~/mem.py
python3 scripts/verify.py       # check your environment
python3 tests/run_all_tests.py  # run the test suite
```

You'll need a Supabase project with `schema.sql` applied and a valid `~/.claude_memory_config.json`.

## Guidelines

- `SKILL.md` must stay under ~6,000 words — Claude loads this in full on activation
- SQL schema changes need a corresponding migration in `scripts/migrate_*.sql`
- New features should include tests in `tests/`
- Update `CHANGELOG.md` under an `[Unreleased]` header
- Python must work on 3.8+; avoid external dependencies beyond `requests`

## Submitting a PR

1. Fork the repo and create a branch off `main`
2. Make your changes
3. Run `python3 tests/run_all_tests.py` — all tests must pass
4. Submit the PR with a short description of what changed and why

## Code of conduct

Keep it focused on the work. Disagreements about approach are fine; personal attacks are not.
