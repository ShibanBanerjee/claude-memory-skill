#!/usr/bin/env python3
"""Test write, read, and delete operations against Supabase."""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

CONFIG_PATH = Path.home() / ".claude_memory_config.json"


def test_storage():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        import requests
    except FileNotFoundError:
        print(f"FAIL: Config file not found at {CONFIG_PATH}")
        return False
    except ImportError:
        print("FAIL: requests library not installed. Run: pip install requests")
        return False

    base_url = f"{cfg['supabase_url'].rstrip('/')}/rest/v1/claude_memories"
    headers = {
        "apikey": cfg["supabase_anon_key"],
        "Authorization": f"Bearer {cfg['supabase_anon_key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    test_id = None
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    unique_title = f"TEST_{str(uuid.uuid4())[:8]}"

    # Write
    try:
        payload = {
            "created_at": ts,
            "updated_at": ts,
            "title": unique_title,
            "project": "_test",
            "conversation_url": "",
            "summary": "This is a test memory entry created by the test suite. It will be deleted immediately after.",
            "key_decisions": ["Test decision — no real decision made — automated test"],
            "open_questions": ["Delete this test entry"],
            "entities": {},
            "tags": ["_test", "automated"],
            "token_count_est": 20,
        }
        r = requests.post(base_url, headers=headers, json=payload, timeout=15)
        if r.status_code >= 400:
            print(f"FAIL write: {r.status_code} — {r.text}")
            return False
        result = r.json()
        stored = result[0] if isinstance(result, list) and result else {}
        test_id = stored.get("id")
        print(f"PASS: Write succeeded — title: {unique_title}, ID: {str(test_id)[:8] if test_id else '?'}")
    except Exception as e:
        print(f"FAIL write: {e}")
        return False

    if not test_id:
        print("WARN: Could not get ID from response — skipping read and delete")
        return True

    # Read back
    try:
        r = requests.get(
            base_url,
            headers={"apikey": cfg["supabase_anon_key"], "Authorization": f"Bearer {cfg['supabase_anon_key']}"},
            params={"id": f"eq.{test_id}", "select": "id,title", "limit": 1},
            timeout=10,
        )
        rows = r.json()
        if not rows:
            print("FAIL: Read returned no results")
            return False
        print(f"PASS: Read succeeded — title: {rows[0].get('title')}")
    except Exception as e:
        print(f"FAIL read: {e}")
        return False

    # Delete
    try:
        r = requests.delete(
            base_url,
            headers={"apikey": cfg["supabase_anon_key"], "Authorization": f"Bearer {cfg['supabase_anon_key']}"},
            params={"id": f"eq.{test_id}"},
            timeout=10,
        )
        if r.status_code < 400:
            print("PASS: Delete succeeded — test data cleaned up")
        else:
            print(f"WARN: Delete returned {r.status_code} — manual cleanup may be needed for ID {str(test_id)[:8]}")
    except Exception as e:
        print(f"WARN: Delete failed ({e}) — manual cleanup may be needed")

    return True


if __name__ == "__main__":
    sys.exit(0 if test_storage() else 1)
