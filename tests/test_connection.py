#!/usr/bin/env python3
"""Test Supabase connectivity."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def test_connection():
    try:
        import requests
    except ImportError:
        print("FAIL: requests not installed")
        return False

    config_path = Path.home() / ".claude_memory_config.json"
    if not config_path.exists():
        print("FAIL: ~/.claude_memory_config.json not found")
        return False

    cfg = json.loads(config_path.read_text())
    key = cfg["supabase_anon_key"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if not key.startswith("sb_"):
        headers["apikey"] = key

    url = cfg["supabase_url"].rstrip("/") + "/rest/v1/claude_memories"
    r = requests.get(url, headers=headers, params={"select": "count", "limit": "1"}, timeout=10)

    if r.status_code == 200:
        print("PASS: Connected to Supabase successfully")
        return True
    else:
        print(f"FAIL: {r.status_code} — {r.text}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_connection() else 1)
