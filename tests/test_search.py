#!/usr/bin/env python3
"""Test full-text search quality."""
import sys, json
from pathlib import Path

def test_search():
    try:
        import requests
    except ImportError:
        print("FAIL: requests not installed"); return False

    cfg = json.loads((Path.home() / ".claude_memory_config.json").read_text())
    key = cfg["supabase_anon_key"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if not key.startswith("sb_"): headers["apikey"] = key
    base = cfg["supabase_url"].rstrip("/") + "/rest/v1"

    r = requests.get(f"{base}/claude_memories", headers=headers,
                     params={"search_vector": "fts.test", "select": "id,title", "limit": "5"}, timeout=10)
    if r.status_code == 200:
        print(f"PASS: Search query succeeded — {len(r.json())} results for 'test'")
        return True
    print(f"FAIL: {r.status_code} — {r.text}")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_search() else 1)
