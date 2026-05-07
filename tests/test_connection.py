#!/usr/bin/env python3
"""Test Supabase database connectivity."""
import sys
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude_memory_config.json"


def test_connection():
    # Check config file
    if not CONFIG_PATH.exists():
        print(f"FAIL: Config file not found at {CONFIG_PATH}")
        print("      Create it with: {\"supabase_url\": \"...\", \"supabase_anon_key\": \"...\"}")
        return False

    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        print(f"FAIL: Config file is not valid JSON: {e}")
        return False

    for key in ("supabase_url", "supabase_anon_key"):
        if not cfg.get(key):
            print(f"FAIL: Missing '{key}' in config file")
            return False

    # Check requests
    try:
        import requests
    except ImportError:
        print("FAIL: requests library not installed. Run: pip install requests")
        return False

    # Connect to Supabase
    url = f"{cfg['supabase_url'].rstrip('/')}/rest/v1/claude_memories"
    headers = {
        "apikey": cfg["supabase_anon_key"],
        "Authorization": f"Bearer {cfg['supabase_anon_key']}",
        "Prefer": "count=exact",
    }

    try:
        r = requests.get(url, headers=headers, params={"select": "id", "limit": 0}, timeout=10)
    except requests.exceptions.ConnectionError as e:
        print(f"FAIL: Could not connect to Supabase: {e}")
        return False
    except requests.exceptions.Timeout:
        print("FAIL: Connection timed out — check if the Supabase project is active (not paused)")
        return False

    if r.status_code == 404:
        print("FAIL: Table 'claude_memories' not found — run schema.sql in your Supabase SQL Editor")
        return False
    if r.status_code == 401:
        print("FAIL: Unauthorized — check your supabase_anon_key in the config file")
        return False
    if r.status_code >= 400:
        print(f"FAIL: Supabase returned {r.status_code}: {r.text}")
        return False

    count_header = r.headers.get("Content-Range", "*/0")
    total = count_header.split("/")[-1] if "/" in count_header else "?"
    print(f"PASS: Connected to {cfg['supabase_url']} — {total} memories stored")
    return True


if __name__ == "__main__":
    sys.exit(0 if test_connection() else 1)
