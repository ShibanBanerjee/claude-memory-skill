#!/usr/bin/env python3
"""Test FTS5 full-text search quality against the local SQLite database."""
import sys
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path.home() / ".claude_memory.db"

SCHEMA_FTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS claude_memories_fts
USING fts5(title, project, summary, tags, content='claude_memories', content_rowid='rowid');

CREATE TRIGGER IF NOT EXISTS memories_ai
AFTER INSERT ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(rowid, title, project, summary, tags)
    VALUES (new.rowid, new.title, new.project, new.summary, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memories_au
AFTER UPDATE ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(claude_memories_fts, rowid, title, project, summary, tags)
    VALUES ('delete', old.rowid, old.title, old.project, old.summary, old.tags);
    INSERT INTO claude_memories_fts(rowid, title, project, summary, tags)
    VALUES (new.rowid, new.title, new.project, new.summary, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad
AFTER DELETE ON claude_memories BEGIN
    INSERT INTO claude_memories_fts(claude_memories_fts, rowid, title, project, summary, tags)
    VALUES ('delete', old.rowid, old.title, old.project, old.summary, old.tags);
END;
"""

def test_search():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    test_id = str(uuid.uuid4())
    unique_term = f"zxqtest{test_id[:6]}"

    try:
        db = sqlite3.connect(DB_PATH)
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript(SCHEMA_FTS)
    except Exception as e:
        print(f"FAIL: Could not connect or init FTS: {e}")
        return False

    # Insert a record with the unique term
    try:
        db.execute(
            "INSERT INTO claude_memories "
            "(id, created_at, updated_at, title, project, conversation_url, "
            " summary, key_decisions, open_questions, entities, tags, token_count_est) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                test_id, ts, ts,
                f"FTS Test {unique_term}",
                "_test",
                "",
                f"This memory contains the unique search term {unique_term} for FTS testing.",
                "[]", "[]", "{}", '["_test"]', 10,
            )
        )
        db.commit()
    except Exception as e:
        print(f"FAIL: Could not insert test record: {e}")
        db.close()
        return False

    # Search via FTS5
    passed = False
    try:
        rows = db.execute(
            "SELECT m.id FROM claude_memories m "
            "WHERE m.rowid IN ("
            "  SELECT rowid FROM claude_memories_fts WHERE claude_memories_fts MATCH ?"
            ")",
            (unique_term,)
        ).fetchall()
        if any(r[0] == test_id for r in rows):
            print(f"PASS: FTS5 search succeeded — test record found by unique term")
            passed = True
        else:
            print("FAIL: FTS5 search ran but test record not found in results")
    except Exception as e:
        print(f"FAIL: FTS5 search error: {e}")

    # Clean up
    try:
        db.execute("DELETE FROM claude_memories WHERE id = ?", (test_id,))
        db.commit()
    except Exception:
        pass
    db.close()
    return passed

if __name__ == "__main__":
    sys.exit(0 if test_search() else 1)
