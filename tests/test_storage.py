#!/usr/bin/env python3
"""Test write and read operations."""
import sys, json, uuid
from pathlib import Path

def test_storage():
    try:
        import requests
    except ImportError:
        print("FAIL: requests not installed"); return False

    cfg = json.loads((Path.home() / ".claude_memory_config.json").read_text())
    key = cfg["supabase_anon_key"]
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "return=representation"}
    if not key.startswith("sb_"): headers["apikey"] = key
    base = cfg["supabase_url"].rstrip("/") + "/rest/v1"

    # Write
    test_id = str(uuid.uuid4())
    payload = {
        "title": f"TEST_{test_id[:8]}",
        "project": "_test",
        "summary": "This is a test memory entry created by the test suite. It should be deleted automatically.",
        "tags": ["_test", "automated"],
        "key_decisions": ["This is a test — no real decision"],
        "open_questions": ["Delete this test entry"],
        "token_count_est": 30
    }
    r = requests.post(f"{base}/claude_memories", headers=headers, json=payload, timeout=15)
    if r.status_code not in (200, 201):
        print(f"FAIL write: {r.status_code} — {r.text}"); return False

    mem_id = r.json()[0]["id"]
    print(f"PASS: Write succeeded — ID: {mem_id}")

    # Read back
    r = requests.get(f"{base}/claude_memories", headers=headers, params={"id": f"eq.{mem_id}"}, timeout=10)
    if r.status_code != 200 or not r.json():
        print("FAIL: Read failed"); return False
    print("PASS: Read succeeded")

    # Delete
    r = requests.delete(f"{base}/claude_memories", headers=headers, params={"id": f"eq.{mem_id}"}, timeout=10)
    if r.status_code in (200, 204):
        print("PASS: Delete succeeded — test data cleaned up")
        return True
    print(f"WARN: Delete returned {r.status_code} — manual cleanup may be needed")
    return True

if __name__ == "__main__":
    sys.exit(0 if test_storage() else 1)
