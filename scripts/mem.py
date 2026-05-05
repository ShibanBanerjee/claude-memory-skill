#!/usr/bin/env python3
"""
Claude Memory Helper — mem.py
Stores and retrieves conversation memories in a local SQLite database.
Zero external dependencies — uses Python standard library only.

Usage:
  python3 mem.py setup                                     init db and print status
  python3 mem.py check  --project "name"                   check if project memory exists
  python3 mem.py store                                     read JSON from stdin, insert new record
  python3 mem.py update --id UUID                          read JSON from stdin, update record
  python3 mem.py search --query "terms" [--project P] [--limit N]
  python3 mem.py list   [--project "name"] [--limit N]
  python3 mem.py get    --id UUID
"""

import sys
import json
import argparse
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8-sig")

DB_PATH = Path.home() / ".claude_memory.db"

# ── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS claude_memories (
    id               TEXT PRIMARY KEY,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    title            TEXT NOT NULL,
    project          TEXT NOT NULL DEFAULT '',
    conversation_url TEXT NOT NULL DEFAULT '',
    summary          TEXT NOT NULL,
    key_decisions    TEXT NOT NULL DEFAULT '[]',
    open_questions   TEXT NOT NULL DEFAULT '[]',
    entities         TEXT NOT NULL DEFAULT '{}',
    tags             TEXT NOT NULL DEFAULT '[]',
    token_count_est  INTEGER NOT NULL DEFAULT 0
);

CREATE VIRTUAL TABLE IF NOT EXISTS claude_memories_fts
USING fts5(
    title, project, summary, tags,
    content='claude_memories',
    content_rowid='rowid'
);

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

# ── DB helpers ───────────────────────────────────────────────────────────────

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db(db):
    db.executescript(SCHEMA)

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def new_id():
    return str(uuid.uuid4())

def deserialize(row):
    d = dict(row)
    for field in ("key_decisions", "open_questions", "entities", "tags"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d

def read_memory_json():
    raw = sys.stdin.read().strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)

def word_count(text):
    return len(text.split()) if text else 0

def serialize_field(value, default):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(default, ensure_ascii=False)

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_setup(args):
    db = connect()
    init_db(db)
    count = db.execute("SELECT COUNT(*) FROM claude_memories").fetchone()[0]
    print("✅ Claude Memory — local database ready")
    print(f"   Location: {DB_PATH}")
    print(f"   Memories stored: {count}")
    db.close()


def cmd_check(args):
    db = connect()
    init_db(db)
    row = db.execute(
        "SELECT id, title, created_at, updated_at "
        "FROM claude_memories WHERE project = ? "
        "ORDER BY updated_at DESC LIMIT 1",
        (args.project,)
    ).fetchone()
    db.close()
    if row:
        print(json.dumps({
            "exists": True,
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }, indent=2))
    else:
        print(json.dumps({"exists": False}))


def cmd_store(args):
    memory = read_memory_json()
    for field in ("title", "summary"):
        if not memory.get(field):
            print(f"ERROR: Memory JSON must include '{field}'", file=sys.stderr)
            sys.exit(1)

    db = connect()
    init_db(db)
    mem_id = new_id()
    ts = now_iso()
    db.execute(
        "INSERT INTO claude_memories "
        "(id, created_at, updated_at, title, project, conversation_url, "
        " summary, key_decisions, open_questions, entities, tags, token_count_est) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            mem_id, ts, ts,
            memory.get("title", ""),
            memory.get("project", ""),
            memory.get("conversation_url", ""),
            memory.get("summary", ""),
            serialize_field(memory.get("key_decisions", []), []),
            serialize_field(memory.get("open_questions", []), []),
            serialize_field(memory.get("entities", {}), {}),
            serialize_field(memory.get("tags", []), []),
            word_count(memory.get("summary", "")),
        )
    )
    db.commit()
    db.close()
    print(json.dumps({
        "status": "stored",
        "id": mem_id,
        "title": memory["title"],
        "created_at": ts,
    }, indent=2))


def cmd_update(args):
    memory = read_memory_json()
    db = connect()
    init_db(db)
    ts = now_iso()
    db.execute(
        "UPDATE claude_memories SET "
        "updated_at=?, title=?, project=?, conversation_url=?, "
        "summary=?, key_decisions=?, open_questions=?, entities=?, tags=?, token_count_est=? "
        "WHERE id=?",
        (
            ts,
            memory.get("title", ""),
            memory.get("project", ""),
            memory.get("conversation_url", ""),
            memory.get("summary", ""),
            serialize_field(memory.get("key_decisions", []), []),
            serialize_field(memory.get("open_questions", []), []),
            serialize_field(memory.get("entities", {}), {}),
            serialize_field(memory.get("tags", []), []),
            word_count(memory.get("summary", "")),
            args.id,
        )
    )
    db.commit()
    changed = db.execute("SELECT changes()").fetchone()[0]
    db.close()
    if changed == 0:
        print(json.dumps({"status": "not_found", "id": args.id}))
        sys.exit(1)
    print(json.dumps({
        "status": "updated",
        "id": args.id,
        "title": memory.get("title", ""),
        "updated_at": ts,
    }, indent=2))


def cmd_search(args):
    query = args.query.strip()
    if not query:
        print("ERROR: --query is required", file=sys.stderr)
        sys.exit(1)

    db = connect()
    init_db(db)

    fts_query = query.replace('"', '""')
    sql = (
        "SELECT * FROM claude_memories "
        "WHERE rowid IN ("
        "  SELECT rowid FROM claude_memories_fts WHERE claude_memories_fts MATCH ?"
        ")"
    )
    params = [fts_query]
    if args.project:
        sql += " AND project = ?"
        params.append(args.project)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(args.limit)

    rows = db.execute(sql, params).fetchall()

    if not rows:
        like = f"%{query}%"
        fallback = (
            "SELECT * FROM claude_memories "
            "WHERE title LIKE ? OR project LIKE ? OR summary LIKE ?"
        )
        fallback_params = [like, like, like]
        if args.project:
            fallback += " AND project = ?"
            fallback_params.append(args.project)
        fallback += " ORDER BY updated_at DESC LIMIT ?"
        fallback_params.append(args.limit)
        rows = db.execute(fallback, fallback_params).fetchall()

    db.close()

    if not rows:
        print(json.dumps({"status": "no_results", "query": query}))
        return

    memories = [deserialize(r) for r in rows]
    print(json.dumps({"status": "found", "count": len(memories), "memories": memories}, indent=2))


def cmd_list(args):
    db = connect()
    init_db(db)
    sql = (
        "SELECT id, created_at, updated_at, title, project, tags, "
        "token_count_est, conversation_url FROM claude_memories"
    )
    params = []
    if args.project:
        sql += " WHERE project = ?"
        params.append(args.project)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    params.append(args.limit)
    rows = db.execute(sql, params).fetchall()
    db.close()
    memories = [deserialize(r) for r in rows]
    print(json.dumps({"count": len(memories), "memories": memories}, indent=2))


def cmd_get(args):
    db = connect()
    init_db(db)
    row = db.execute("SELECT * FROM claude_memories WHERE id = ?", (args.id,)).fetchone()
    db.close()
    if not row:
        print(json.dumps({"status": "not_found", "id": args.id}))
        sys.exit(1)
    print(json.dumps(deserialize(row), indent=2))

# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Claude Memory Helper — local SQLite storage")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("setup")

    s_check = sub.add_parser("check")
    s_check.add_argument("--project", required=True)

    sub.add_parser("store")

    s_update = sub.add_parser("update")
    s_update.add_argument("--id", required=True)

    s_search = sub.add_parser("search")
    s_search.add_argument("--query", required=True)
    s_search.add_argument("--project", default="")
    s_search.add_argument("--limit", type=int, default=5)

    s_list = sub.add_parser("list")
    s_list.add_argument("--project", default="")
    s_list.add_argument("--limit", type=int, default=20)

    s_get = sub.add_parser("get")
    s_get.add_argument("--id", required=True)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)

    {
        "setup":  cmd_setup,
        "check":  cmd_check,
        "store":  cmd_store,
        "update": cmd_update,
        "search": cmd_search,
        "list":   cmd_list,
        "get":    cmd_get,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
