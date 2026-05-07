#!/usr/bin/env python3
"""
claude-memory-skill — Installation Verifier
Run: python3 scripts/verify.py
"""

import sys
import subprocess
from pathlib import Path

PASS = "OK"
FAIL = "FAIL"

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


def check_requests():
    try:
        import requests  # noqa: F401
        import importlib.metadata
        version = importlib.metadata.version("requests")
        return f"requests {version}"
    except ImportError:
        raise Exception(
            "requests not installed. Run: pip install requests"
        )


def check_mem_py():
    mem_path = Path.home() / "mem.py"
    if not mem_path.exists():
        raise Exception(
            f"mem.py not found at {mem_path}\n"
            "Install with: curl -o ~/mem.py https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem.py"
        )
    return f"Found at {mem_path}"


def check_config():
    config_path = Path.home() / ".claude_memory_config.json"
    if not config_path.exists():
        raise Exception(
            f"Config not found at {config_path}\n"
            'Create it: {"supabase_url": "https://xxx.supabase.co", "supabase_anon_key": "your-key"}'
        )
    import json
    with open(config_path) as f:
        cfg = json.load(f)
    for key in ("supabase_url", "supabase_anon_key"):
        if not cfg.get(key):
            raise Exception(f"Missing '{key}' in {config_path}")
    return f"Found at {config_path}"


def check_connection():
    result = subprocess.run(
        [sys.executable, str(Path.home() / "mem.py"), "setup"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        raise Exception(result.stderr.strip() or "mem.py setup failed")
    first_line = result.stdout.strip().split("\n")[0]
    return first_line


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

check("Python version",        check_python_version)
check("requests installed",    check_requests)
check("mem.py installed",      check_mem_py)
check("Config file",           check_config)
check("Supabase connection",   check_connection)
check("SKILL.md installed",    check_skill_md)

print()
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)

for status, name, detail in results:
    marker = "[OK]  " if status == PASS else "[FAIL]"
    detail_str = f" — {detail}" if detail else ""
    print(f"  {marker} {name}{detail_str}")

print()
print(f"Results: {passed} passed, {failed} failed")
print()

if failed == 0:
    print("Everything looks good. Try /mem in any Claude conversation.")
else:
    print("Some checks failed. See docs/TROUBLESHOOTING.md for help.")
print()
