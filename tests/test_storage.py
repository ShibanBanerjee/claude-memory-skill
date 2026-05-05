#!/usr/bin/env python3
"""Test write, read, and delete operations against the local SQLite database."""
import sys
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path.home() / ".claude_memory.db"

def test_storage():
    test_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
    except Exception as e:
        print(f"FAIL: Could not connect to database at {DB_PATH}: {e}")
        return False

    # Write
    try:
        db.execute(
            "INSERT INTO claude_memories "
            "(id, created_at, updated_at, title, project, conversation_url, "
            " summary, key_decisions, open_questions, entities, tags, token_count_est) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                test_id, ts, ts,
                f"TEST_{test_id[:8]}",
                "_test",
                "",
                "This is a test memory entry created by the test suite. It will be deleted.",
                '["Test decision — no real decision made"]',
                '["Delete this test entry"]',
                "{}",
                '["_test", "automated"]',
                12,
            )
        )
        db.commit()
        print(f"PASS: Write succeeded — ID: {test_id[:8]}")
    except Exception as e:
        print(f"FAIL write: {e}")
        db.close()
        return False

    # Read back
    try:
        row = db.execute(
            "SELECT id, title FROM claude_memories WHERE id = ?", (test_id,)
        ).fetchone()
        if not row:
            print("FAIL: Read returned no results")
            db.close()
            return False
        print(f"PASS: Read succeeded — title: {row['title']}")
    except Exception as e:
        print(f"FAIL read: {e}")
        db.close()
        return False

    # Delete
    try:
        db.execute("DELETE FROM claude_memories WHERE id = ?", (test_id,))
        db.commit()
        print("PASS: Delete succeeded — test data cleaned up")
    except Exception as e:
        print(f"WARN: Delete failed ({e}) — manual cleanup may be needed for ID {test_id[:8]}")

    db.close()
    return True

if __name__ == "__main__":
    sys.exit(0 if test_storage() else 1)
