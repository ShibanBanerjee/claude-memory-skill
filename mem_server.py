#!/usr/bin/env python3
"""
Claude Memory Server — mem_server.py
Local HTTP server exposing Claude memory over localhost.
Enables Claude Desktop on Windows (and all platforms) to access
memories stored on the real host machine, even from inside a container.

Run once on your machine — leave it running in the background.
Claude calls it via curl. No external dependencies. Pure Python stdlib.

Usage:
  python mem_server.py              # Start on default port 7823
  python mem_server.py --port 8080  # Custom port
  python mem_server.py --host 127.0.0.1  # Restrict to loopback only

Endpoints (all return JSON):
  GET  /health                           Server status + memory count
  GET  /setup                            Init DB + return status
  GET  /check?project=slug               Check if project memory exists
  GET  /list?limit=20&project=optional   List all memories
  GET  /search?query=term&limit=5        Full-text search
  GET  /get?id=uuid                      Get single memory by ID
  POST /store                            Store new memory (JSON body)
  POST /update?id=uuid                   Update existing memory (JSON body)
"""

import sys
import json
import sqlite3
import uuid
import argparse
import threading
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Config ───────────────────────────────────────────────────────────────────

DEFAULT_PORT = 7823
DEFAULT_HOST = "0.0.0.0"   # Accept connections from container (host.docker.internal)
DB_PATH = Path.home() / ".claude_memory.db"

# ── Schema (identical to mem.py) ─────────────────────────────────────────────

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

# ── DB helpers ────────────────────────────────────────────────────────────────

_db_lock = threading.Lock()

def connect():
    db = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with _db_lock:
        db = connect()
        db.executescript(SCHEMA)
        db.close()

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def new_id():
    return str(uuid.uuid4())

def word_count(text):
    return len(text.split()) if text else 0

def serialize(value, default):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(default, ensure_ascii=False)

def deserialize(row):
    d = dict(row)
    for field in ("key_decisions", "open_questions", "entities", "tags"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d

def memory_count():
    with _db_lock:
        db = connect()
        count = db.execute("SELECT COUNT(*) FROM claude_memories").fetchone()[0]
        db.close()
        return count

# ── Request handler ───────────────────────────────────────────────────────────

class MemoryHandler(BaseHTTPRequestHandler):

    # ── Routing ──────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        routes = {
            "/health": self.handle_health,
            "/setup":  self.handle_setup,
            "/check":  self.handle_check,
            "/list":   self.handle_list,
            "/search": self.handle_search,
            "/get":    self.handle_get,
        }
        handler = routes.get(parsed.path)
        if handler:
            try:
                handler(params)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_json({"error": "Not found", "path": parsed.path}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError as e:
            self.send_json({"error": f"Invalid JSON body: {e}"}, 400)
            return

        routes = {
            "/store":  self.handle_store,
            "/update": self.handle_update,
        }
        handler = routes.get(parsed.path)
        if handler:
            try:
                handler(params, body)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_json({"error": "Not found", "path": parsed.path}, 404)

    # ── GET handlers ─────────────────────────────────────────────────────────

    def handle_health(self, params):
        self.send_json({
            "status": "ok",
            "db": str(DB_PATH),
            "memories": memory_count(),
            "version": "2.0.0",
        })

    def handle_setup(self, params):
        init_db()
        self.send_json({
            "status": "ready",
            "db": str(DB_PATH),
            "memories": memory_count(),
        })

    def handle_check(self, params):
        project = params.get("project", [""])[0]
        if not project:
            self.send_json({"error": "project param required"}, 400)
            return
        with _db_lock:
            db = connect()
            row = db.execute(
                "SELECT id, title, created_at, updated_at FROM claude_memories "
                "WHERE project = ? ORDER BY updated_at DESC LIMIT 1",
                (project,)
            ).fetchone()
            db.close()
        if row:
            self.send_json({
                "exists": True,
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
        else:
            self.send_json({"exists": False})

    def handle_list(self, params):
        limit = int(params.get("limit", [20])[0])
        project = params.get("project", [""])[0]
        with _db_lock:
            db = connect()
            if project:
                rows = db.execute(
                    "SELECT id, created_at, updated_at, title, project, tags, "
                    "token_count_est, conversation_url FROM claude_memories "
                    "WHERE project = ? ORDER BY updated_at DESC LIMIT ?",
                    (project, limit)
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT id, created_at, updated_at, title, project, tags, "
                    "token_count_est, conversation_url FROM claude_memories "
                    "ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
            db.close()
        self.send_json({"count": len(rows), "memories": [deserialize(r) for r in rows]})

    def handle_search(self, params):
        query = params.get("query", [""])[0].strip()
        limit = int(params.get("limit", [5])[0])
        project = params.get("project", [""])[0]
        if not query:
            self.send_json({"error": "query param required"}, 400)
            return

        with _db_lock:
            db = connect()
            fts_query = query.replace('"', '""')
            sql = (
                "SELECT * FROM claude_memories "
                "WHERE rowid IN ("
                "  SELECT rowid FROM claude_memories_fts WHERE claude_memories_fts MATCH ?"
                ")"
            )
            sql_params = [fts_query]
            if project:
                sql += " AND project = ?"
                sql_params.append(project)
            sql += " ORDER BY updated_at DESC LIMIT ?"
            sql_params.append(limit)
            rows = db.execute(sql, sql_params).fetchall()

            if not rows:
                like = f"%{query}%"
                fb_sql = (
                    "SELECT * FROM claude_memories "
                    "WHERE title LIKE ? OR project LIKE ? OR summary LIKE ?"
                )
                fb_params = [like, like, like]
                if project:
                    fb_sql += " AND project = ?"
                    fb_params.append(project)
                fb_sql += " ORDER BY updated_at DESC LIMIT ?"
                fb_params.append(limit)
                rows = db.execute(fb_sql, fb_params).fetchall()
            db.close()

        if not rows:
            self.send_json({"status": "no_results", "query": query})
            return
        self.send_json({
            "status": "found",
            "count": len(rows),
            "memories": [deserialize(r) for r in rows],
        })

    def handle_get(self, params):
        mem_id = params.get("id", [""])[0]
        if not mem_id:
            self.send_json({"error": "id param required"}, 400)
            return
        with _db_lock:
            db = connect()
            row = db.execute(
                "SELECT * FROM claude_memories WHERE id = ?", (mem_id,)
            ).fetchone()
            db.close()
        if not row:
            self.send_json({"status": "not_found", "id": mem_id}, 404)
            return
        self.send_json(deserialize(row))

    # ── POST handlers ─────────────────────────────────────────────────────────

    def handle_store(self, params, memory):
        for field in ("title", "summary"):
            if not memory.get(field):
                self.send_json({"error": f"'{field}' is required"}, 400)
                return

        mem_id = new_id()
        ts = now_iso()
        with _db_lock:
            db = connect()
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
                    serialize(memory.get("key_decisions", []), []),
                    serialize(memory.get("open_questions", []), []),
                    serialize(memory.get("entities", {}), {}),
                    serialize(memory.get("tags", []), []),
                    word_count(memory.get("summary", "")),
                )
            )
            db.commit()
            db.close()
        self.send_json({
            "status": "stored",
            "id": mem_id,
            "title": memory["title"],
            "created_at": ts,
        })

    def handle_update(self, params, memory):
        mem_id = params.get("id", [""])[0]
        if not mem_id:
            self.send_json({"error": "id param required"}, 400)
            return
        ts = now_iso()
        with _db_lock:
            db = connect()
            db.execute(
                "UPDATE claude_memories SET "
                "updated_at=?, title=?, project=?, conversation_url=?, "
                "summary=?, key_decisions=?, open_questions=?, entities=?, "
                "tags=?, token_count_est=? WHERE id=?",
                (
                    ts,
                    memory.get("title", ""),
                    memory.get("project", ""),
                    memory.get("conversation_url", ""),
                    memory.get("summary", ""),
                    serialize(memory.get("key_decisions", []), []),
                    serialize(memory.get("open_questions", []), []),
                    serialize(memory.get("entities", {}), {}),
                    serialize(memory.get("tags", []), []),
                    word_count(memory.get("summary", "")),
                    mem_id,
                )
            )
            db.commit()
            changed = db.execute("SELECT changes()").fetchone()[0]
            db.close()
        if changed == 0:
            self.send_json({"status": "not_found", "id": mem_id}, 404)
            return
        self.send_json({
            "status": "updated",
            "id": mem_id,
            "title": memory.get("title", ""),
            "updated_at": ts,
        })

    # ── Helpers ───────────────────────────────────────────────────────────────

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # Silent — no terminal noise


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Claude Memory Server — local HTTP API for mem.py"
    )
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help=f"Bind address (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port (default: {DEFAULT_PORT})")
    args = parser.parse_args()

    init_db()
    count = memory_count()

    server = HTTPServer((args.host, args.port), MemoryHandler)

    print(f"✅ Claude Memory Server running")
    print(f"   Database : {DB_PATH}")
    print(f"   Memories : {count}")
    print(f"   Listening: http://{args.host}:{args.port}")
    print(f"   Health   : http://localhost:{args.port}/health")
    print(f"   Stop     : Ctrl+C")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
