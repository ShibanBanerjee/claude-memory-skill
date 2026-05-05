#!/usr/bin/env python3
"""
claude-memory-skill — Installation Verifier
Run: python3 scripts/verify.py
"""

import sys
import json
import os
from pathlib import Path

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

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
    import requests
    return f"requests {requests.__version__}"

def check_config():
    config_path = Path.home() / ".claude_memory_config.json"
    if not config_path.exists():
        raise Exception(f"Config not found at {config_path}")
    config = json.loads(config_path.read_text())
    if "supabase_url" not in config:
        raise Exception("Missing 'supabase_url' in config")
    if "supabase_anon_key" not in config:
        raise Exception("Missing 'supabase_anon_key' in config")
    url = config["supabase_url"]
    key = config["supabase_anon_key"]
    if not url.startswith("https://"):
        raise Exception("supabase_url must start with https://")
    key_type = "legacy anon (JWT)" if key.startswith("eyJ") else "publishable (may fail from server)"
    return f"Found. Key type: {key_type}"

def check_mem_py():
    mem_path = Path.home() / "mem.py"
    if not mem_path.exists():
        raise Exception(f"mem.py not found at {mem_path}. Run: cp mem.py ~/mem.py")
    return f"Found at {mem_path}"

def check_supabase_connection():
    import requests as req
    config_path = Path.home() / ".claude_memory_config.json"
    config = json.loads(config_path.read_text())
    url = config["supabase_url"].rstrip("/") + "/rest/v1/claude_memories"
    key = config["supabase_anon_key"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    if key.startswith("sb_"):
        headers = {"Authorization": f"Bearer {key}"}
    r = req.get(url, headers=headers, params={"select": "id", "limit": "1"}, timeout=10)
    if r.status_code == 200:
        return "Connected to Supabase successfully"
    elif r.status_code == 404:
        raise Exception("Table 'claude_memories' not found. Run schema.sql in Supabase SQL Editor.")
    elif r.status_code == 403:
        raise Exception(f"403 Forbidden: {r.text}. Try using legacy anon key (eyJ...) instead of publishable key.")
    else:
        raise Exception(f"HTTP {r.status_code}: {r.text}")

def check_skill_md():
    skill_path = Path("/mnt/skills/user/claude-memory/SKILL.md")
    if skill_path.exists():
        return f"Installed at {skill_path}"
    # Check other common locations
    alt_paths = [
        Path("/mnt/skills/user/mem-skill/SKILL.md"),
        Path.home() / "claude-skills" / "SKILL.md",
    ]
    for p in alt_paths:
        if p.exists():
            return f"Found at {p} (non-standard location)"
    raise Exception("SKILL.md not found in Claude skills directory. Copy it manually.")

print()
print("claude-memory-skill — Installation Verifier")
print("=" * 50)
print()

check("Python version", check_python_version)
check("requests library", check_requests)
check("Config file", check_config)
check("mem.py installed", check_mem_py)
check("Supabase connection", check_supabase_connection)
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
    print("Everything looks good! Try /mem in any Claude conversation.")
else:
    print("Some checks failed. See docs/troubleshooting.md for help.")
print()
