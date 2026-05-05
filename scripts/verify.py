#!/usr/bin/env python3
"""
claude-memory-skill — Installation Verifier
Run: python3 scripts/verify.py
"""

import sys
import sqlite3
import subprocess
from pathlib import Path

PASS = "✅"
FAIL = "❌"

results = []

def check(name, fn):
    try:
        result = fn()
        if result is True:
            results.append((PASS, name, ""))
        elif isinstance(result, str):
            results.append((PASS, name, result))
    except Exception as e:
        results.append((FAIL, name, str(e)))

def check_python_version():
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 8):
        raise Exception(f"Python 3.8+ required, found {major}.{minor}")
    return f"Python {major}.{minor}"

def check_sqlite_fts5():
    version = sqlite3.sqlite_version
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
    except sqlite3.OperationalError:
        raise Exception(
            f"SQLite {version} — FTS5 not available in this build. "
            "Try the Python from python.org or install libsqlite3-dev."
        )
    finally:
        db.close()
    return f"SQLite {version} with FTS5"

def check_mem_py():
    mem_path = Path.home() / "mem.py"
    if not mem_path.exists():
        raise Exception(
            f"mem.py not found at {mem_path}\n"
            "Install with: cp scripts/mem.py ~/mem.py"
        )
    return f"Found at {mem_path}"

def check_database():
    result = subprocess.run(
        [sys.executable, str(Path.home() / "mem.py"), "setup"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        raise Exception(result.stderr.strip() or "mem.py setup failed")
    first_line = result.stdout.strip().split("\n")[0]
    return first_line.replace("✅ ", "")

def check_skill_md():
    candidates = [
        Path.home() / ".claude" / "skills" / "claude-memory" / "SKILL.md",
        Path("/mnt/skills/user/claude-memory/SKILL.md"),
    ]
    for p in candidates:
        if p.exists():
            return f"Found at {p}"
    raise Exception(
        "SKILL.md not found. Install with:\n"
        "  mkdir -p ~/.claude/skills/claude-memory\n"
        "  cp SKILL.md ~/.claude/skills/claude-memory/SKILL.md"
    )


print()
print("claude-memory-skill — Installation Verifier")
print("=" * 50)
print()

check("Python version",     check_python_version)
check("SQLite + FTS5",      check_sqlite_fts5)
check("mem.py installed",   check_mem_py)
check("Database ready",     check_database)
check("SKILL.md installed", check_skill_md)

print()
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)

for status, name, detail in results:
    detail_str = f" — {detail}" if detail else ""
    print(f"  {status} {name}{detail_str}")

print()
print(f"Results: {passed} passed, {failed} failed")
print()

if failed == 0:
    print("Everything looks good. Try /mem in any Claude conversation.")
else:
    print("Some checks failed. See docs/TROUBLESHOOTING.md for help.")
print()
