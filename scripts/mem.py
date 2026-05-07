#!/usr/bin/env python3
"""
Claude Memory Helper — mem.py
Stores and retrieves conversation memories using Supabase PostgreSQL.

Requires: pip install requests

Configuration: ~/.claude_memory_config.json
  {
    "supabase_url": "https://your-project.supabase.co",
    "supabase_anon_key": "your-anon-key"
  }

Usage:
  python3 mem.py setup                                     verify connection and print status
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
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print(
        "ERROR: 'requests' library not found. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(1)

CONFIG_PATH = Path.home() / ".claude_memory_config.json"
TABLE = "claude_memories"


# ── Config ────────────────────────────────────────────────────────────────────

def load_config():
    if not CONFIG_PATH.exists():
        print(f"ERROR: Config file not found: {CONFIG_PATH}", file=sys.stderr)
        print("Create it with your Supabase credentials:", file=sys.stderr)
        print(
            '  {"supabase_url": "https://xxx.supabase.co", "supabase_anon_key": "your-anon-key"}',
            file=sys.stderr,
        )
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for key in ("supabase_url", "supabase_anon_key"):
        if not cfg.get(key):
            print(f"ERROR: Missing '{key}' in {CONFIG_PATH}", file=sys.stderr)
            sys.exit(1)
    return cfg


def api_base(cfg):
    return f"{cfg['supabase_url'].rstrip('/')}/rest/v1/{TABLE}"


def default_headers(cfg, extra=None):
    h = {
        "apikey": cfg["supabase_anon_key"],
        "Authorization": f"Bearer {cfg['supabase_anon_key']}",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


# ── Helpers ───────────────────────────────────────────────────────────────────

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def word_count(text):
    return len(text.split()) if text else 0


def read_memory_json():
    raw = sys.stdin.read().strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)


def check_response(r, context=""):
    if r.status_code >= 400:
        msg = f"ERROR: Supabase API error ({r.status_code})"
        if context:
            msg += f" — {context}"
        msg += f": {r.text}"
        print(msg, file=sys.stderr)
        sys.exit(1)
    return r


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_setup(args):
    cfg = load_config()
    r = requests.get(
        api_base(cfg),
        headers=default_headers(cfg, {"Prefer": "count=exact"}),
        params={"select": "id", "limit": 0},
        timeout=10,
    )
    check_response(r, "setup")
    content_range = r.headers.get("Content-Range", "*/0")
    total = content_range.split("/")[-1] if "/" in content_range else "?"
    print("Claude Memory — Supabase ready")
    print(f"   Project: {cfg['supabase_url']}")
    print(f"   Memories stored: {total}")


def cmd_check(args):
    cfg = load_config()
    r = requests.get(
        api_base(cfg),
        headers=default_headers(cfg),
        params={
            "select": "id,title,created_at,updated_at",
            "project": f"eq.{args.project}",
            "order": "updated_at.desc",
            "limit": 1,
        },
        timeout=10,
    )
    check_response(r, "check")
    rows = r.json()
    if rows:
        row = rows[0]
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

    cfg = load_config()
    ts = now_iso()
    payload = {
        "created_at": ts,
        "updated_at": ts,
        "title": memory.get("title", ""),
        "project": memory.get("project", ""),
        "conversation_url": memory.get("conversation_url", ""),
        "summary": memory.get("summary", ""),
        "key_decisions": memory.get("key_decisions", []),
        "open_questions": memory.get("open_questions", []),
        "entities": memory.get("entities", {}),
        "tags": memory.get("tags", []),
        "token_count_est": word_count(memory.get("summary", "")),
    }
    r = requests.post(
        api_base(cfg),
        headers=default_headers(cfg, {"Prefer": "return=representation"}),
        json=payload,
        timeout=15,
    )
    check_response(r, "store")
    result = r.json()
    stored = result[0] if isinstance(result, list) and result else payload
    print(json.dumps({
        "status": "stored",
        "id": stored.get("id", ""),
        "title": stored.get("title", memory.get("title", "")),
        "created_at": stored.get("created_at", ts),
    }, indent=2))


def cmd_update(args):
    memory = read_memory_json()
    cfg = load_config()
    ts = now_iso()
    payload = {
        "updated_at": ts,
        "title": memory.get("title", ""),
        "project": memory.get("project", ""),
        "conversation_url": memory.get("conversation_url", ""),
        "summary": memory.get("summary", ""),
        "key_decisions": memory.get("key_decisions", []),
        "open_questions": memory.get("open_questions", []),
        "entities": memory.get("entities", {}),
        "tags": memory.get("tags", []),
        "token_count_est": word_count(memory.get("summary", "")),
    }
    r = requests.patch(
        api_base(cfg),
        headers=default_headers(cfg, {"Prefer": "return=representation"}),
        params={"id": f"eq.{args.id}"},
        json=payload,
        timeout=15,
    )
    check_response(r, "update")
    result = r.json()
    if not result:
        print(json.dumps({"status": "not_found", "id": args.id}))
        sys.exit(1)
    stored = result[0] if isinstance(result, list) else result
    print(json.dumps({
        "status": "updated",
        "id": args.id,
        "title": stored.get("title", memory.get("title", "")),
        "updated_at": ts,
    }, indent=2))


def cmd_search(args):
    query = args.query.strip()
    if not query:
        print("ERROR: --query is required", file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    rows = []

    # Attempt 1: PostgreSQL full-text search via search_vector column
    params_fts = {
        "select": "*",
        "search_vector": f"plfts.{query}",
        "order": "updated_at.desc",
        "limit": args.limit,
    }
    if args.project:
        params_fts["project"] = f"eq.{args.project}"
    r = requests.get(api_base(cfg), headers=default_headers(cfg), params=params_fts, timeout=10)
    if r.status_code == 200:
        rows = r.json()

    # Attempt 2: LIKE fallback across title, project, summary
    if not rows:
        like_q = query.replace("'", "''")
        params_like = {
            "select": "*",
            "or": f"(title.ilike.*{like_q}*,project.ilike.*{like_q}*,summary.ilike.*{like_q}*)",
            "order": "updated_at.desc",
            "limit": args.limit,
        }
        if args.project:
            params_like["project"] = f"eq.{args.project}"
        r2 = requests.get(
            api_base(cfg), headers=default_headers(cfg), params=params_like, timeout=10
        )
        if r2.status_code == 200:
            rows = r2.json()

    if not rows:
        print(json.dumps({"status": "no_results", "query": query}))
        return

    print(json.dumps({"status": "found", "count": len(rows), "memories": rows}, indent=2))


def cmd_list(args):
    cfg = load_config()
    params = {
        "select": "id,created_at,updated_at,title,project,tags,token_count_est,conversation_url",
        "order": "updated_at.desc",
        "limit": args.limit,
    }
    if args.project:
        params["project"] = f"eq.{args.project}"
    r = requests.get(api_base(cfg), headers=default_headers(cfg), params=params, timeout=10)
    check_response(r, "list")
    rows = r.json()
    print(json.dumps({"count": len(rows), "memories": rows}, indent=2))


def cmd_get(args):
    cfg = load_config()
    r = requests.get(
        api_base(cfg),
        headers=default_headers(cfg),
        params={"id": f"eq.{args.id}", "select": "*", "limit": 1},
        timeout=10,
    )
    check_response(r, "get")
    rows = r.json()
    if not rows:
        print(json.dumps({"status": "not_found", "id": args.id}))
        sys.exit(1)
    print(json.dumps(rows[0], indent=2))


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Claude Memory Helper — Supabase storage")
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
