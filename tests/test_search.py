#!/usr/bin/env python3
"""Test full-text search quality against Supabase."""
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

CONFIG_PATH = Path.home() / ".claude_memory_config.json"


def test_search():
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
    write_headers = {
        "apikey": cfg["supabase_anon_key"],
        "Authorization": f"Bearer {cfg['supabase_anon_key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    read_headers = {
        "apikey": cfg["supabase_anon_key"],
        "Authorization": f"Bearer {cfg['supabase_anon_key']}",
    }

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    unique_term = f"zxqtest{str(uuid.uuid4())[:6]}"
    test_id = None

    # Insert a record with the unique term in the summary
    try:
        payload = {
            "created_at": ts,
            "updated_at": ts,
            "title": f"FTS Test {unique_term}",
            "project": "_test",
            "conversation_url": "",
            "summary": f"This memory contains the unique search term {unique_term} for FTS testing purposes.",
            "key_decisions": [],
            "open_questions": [],
            "entities": {},
            "tags": ["_test"],
            "token_count_est": 15,
        }
        r = requests.post(base_url, headers=write_headers, json=payload, timeout=15)
        if r.status_code >= 400:
            print(f"FAIL: Could not insert test record: {r.status_code} — {r.text}")
            return False
        result = r.json()
        stored = result[0] if isinstance(result, list) and result else {}
        test_id = stored.get("id")
    except Exception as e:
        print(f"FAIL: Could not insert test record: {e}")
        return False

    passed = False

    # Search via full-text search on search_vector
    try:
        r = requests.get(
            base_url,
            headers=read_headers,
            params={
                "select": "id",
                "search_vector": f"plfts.{unique_term}",
                "limit": 5,
            },
            timeout=10,
        )
        rows = r.json() if r.status_code == 200 else []
        if test_id and any(row.get("id") == test_id for row in rows):
            print("PASS: Full-text search succeeded — test record found by unique term")
            passed = True
        else:
            # Try LIKE fallback
            r2 = requests.get(
                base_url,
                headers=read_headers,
                params={
                    "select": "id",
                    "or": f"(title.ilike.*{unique_term}*,summary.ilike.*{unique_term}*)",
                    "limit": 5,
                },
                timeout=10,
            )
            rows2 = r2.json() if r2.status_code == 200 else []
            if test_id and any(row.get("id") == test_id for row in rows2):
                print("PASS: LIKE fallback search succeeded — test record found by unique term")
                passed = True
            else:
                print("FAIL: Neither FTS nor LIKE search found the test record")
    except Exception as e:
        print(f"FAIL: Search error: {e}")

    # Clean up
    if test_id:
        try:
            requests.delete(
                base_url,
                headers=read_headers,
                params={"id": f"eq.{test_id}"},
                timeout=10,
            )
        except Exception:
            pass

    return passed


if __name__ == "__main__":
    sys.exit(0 if test_search() else 1)
