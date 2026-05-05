#!/usr/bin/env python3
"""Test SQLite database connectivity and FTS5 availability."""
import sys
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".claude_memory.db"

def test_connection():
    # Verify FTS5 is available
    try:
        db = sqlite3.connect(":memory:")
        db.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        db.close()
    except sqlite3.OperationalError:
        print(f"FAIL: SQLite FTS5 not available (SQLite {sqlite3.sqlite_version})")
        return False

    # Connect to the real database and ensure schema exists
    try:
        db = sqlite3.connect(DB_PATH)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("""
            CREATE TABLE IF NOT EXISTS claude_memories (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                title TEXT NOT NULL, project TEXT NOT NULL DEFAULT '',
                conversation_url TEXT NOT NULL DEFAULT '', summary TEXT NOT NULL,
                key_decisions TEXT NOT NULL DEFAULT '[]', open_questions TEXT NOT NULL DEFAULT '[]',
                entities TEXT NOT NULL DEFAULT '{}', tags TEXT NOT NULL DEFAULT '[]',
                token_count_est INTEGER NOT NULL DEFAULT 0
            )
        """)
        db.commit()
        count = db.execute("SELECT COUNT(*) FROM claude_memories").fetchone()[0]
        db.close()
        print(f"PASS: Connected to {DB_PATH} — {count} memories stored (SQLite {sqlite3.sqlite_version} + FTS5)")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_connection() else 1)
