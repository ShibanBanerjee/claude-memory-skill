#!/usr/bin/env python3
"""
Claude Memory Helper — mem.py
Called by the /mem skill to compress conversations and store/retrieve memories.
Usage:
  python3 mem.py store  --title "..." --project "..." --conv-id "..." --conv-url "..."
  python3 mem.py search --query "..."
  python3 mem.py list   [--project "..."] [--limit N]
  python3 mem.py get    --id "..."
  python3 mem.py setup  (test connection and print config path)
"""

import sys, os, json, re, textwrap, argparse
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests --break-system-packages")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────────
CONFIG_PATH = Path.home() / ".claude_memory_config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print(f"""
ERROR: Config file not found at {CONFIG_PATH}

Create it with your Supabase credentials:
{{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "YOUR_ANON_KEY"
}}

Find these in: Supabase Dashboard → Project Settings → API
""")
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text())

def headers(cfg):
    key = cfg["supabase_anon_key"]
    # New publishable key format (sb_publishable_...) — Authorization only
    # Legacy anon JWT format (eyJ...) — both apikey + Authorization
    if key.startswith("sb_"):
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def base_url(cfg):
    return cfg["supabase_url"].rstrip("/") + "/rest/v1"

# ── Store ────────────────────────────────────────────────────────────────────
def cmd_store(args, cfg):
    """Read compressed memory JSON from stdin and store in Supabase."""
    raw = sys.stdin.read().strip()
    try:
        memory = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from stdin: {e}")
        print("Received:", raw[:500])
        sys.exit(1)

    # Merge CLI args into memory object
    if args.title:   memory["title"]            = args.title
    if args.project: memory["project"]          = args.project
    if args.conv_id: memory["conversation_id"]  = args.conv_id
    if args.conv_url:memory["conversation_url"] = args.conv_url

    # Validate required fields
    required = ["title", "summary"]
    for f in required:
        if not memory.get(f):
            print(f"ERROR: Memory JSON must include '{f}'")
            sys.exit(1)

    # Estimate token count (rough: 1 token ≈ 4 chars)
    memory["token_count_est"] = len(memory.get("summary", "")) // 4

    # POST to Supabase
    r = requests.post(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        json=memory,
        timeout=15
    )
    if r.status_code not in (200, 201):
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    result = r.json()
    if isinstance(result, list): result = result[0]
    print(json.dumps({
        "status": "stored",
        "id": result.get("id"),
        "title": result.get("title"),
        "created_at": result.get("created_at"),
    }, indent=2))

# ── Search ───────────────────────────────────────────────────────────────────
def cmd_search(args, cfg):
    """Full-text search memories."""
    query = args.query.strip()
    if not query:
        print("ERROR: --query required")
        sys.exit(1)

    # Build FTS query (AND between words)
    ts_query = " & ".join(re.sub(r'[^\w\s]', '', query).split())

    params = {
        "select": "id,created_at,title,project,tags,summary,key_decisions,open_questions,conversation_url",
        "search_vector": f"fts.{ts_query}",
        "order": "created_at.desc",
        "limit": str(args.limit or 5),
    }
    if args.project:
        params["project"] = f"eq.{args.project}"

    r = requests.get(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        params=params,
        timeout=15
    )
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    results = r.json()
    if not results:
        print(json.dumps({"status": "no_results", "query": query}))
        return

    # Format for Claude consumption
    output = []
    for m in results:
        output.append({
            "id": m["id"],
            "date": m["created_at"][:10],
            "title": m["title"],
            "project": m.get("project"),
            "tags": m.get("tags", []),
            "summary": m["summary"],
            "key_decisions": m.get("key_decisions", []),
            "open_questions": m.get("open_questions", []),
            "url": m.get("conversation_url"),
        })

    print(json.dumps({"status": "found", "count": len(output), "memories": output}, indent=2))

# ── List ─────────────────────────────────────────────────────────────────────
def cmd_list(args, cfg):
    """List recent memories (compact cards)."""
    params = {
        "select": "id,created_at,title,project,tags,conversation_url",
        "order": "created_at.desc",
        "limit": str(args.limit or 10),
    }
    if args.project:
        params["project"] = f"eq.{args.project}"

    r = requests.get(
        f"{base_url(cfg)}/memory_cards",
        headers=headers(cfg),
        params=params,
        timeout=15
    )
    if r.status_code != 200:
        # Fallback to raw table if view not created
        r = requests.get(
            f"{base_url(cfg)}/claude_memories",
            headers=headers(cfg),
            params=params,
            timeout=15
        )
    results = r.json()
    print(json.dumps({"count": len(results), "memories": results}, indent=2))

# ── Get ──────────────────────────────────────────────────────────────────────
def cmd_get(args, cfg):
    """Retrieve a single memory by ID."""
    r = requests.get(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        params={"id": f"eq.{args.id}", "select": "*"},
        timeout=15
    )
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)
    results = r.json()
    if not results:
        print(json.dumps({"status": "not_found", "id": args.id}))
        return
    print(json.dumps(results[0], indent=2))

# ── Setup ────────────────────────────────────────────────────────────────────
def cmd_setup(args, cfg):
    """Test connection and print status."""
    r = requests.get(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        params={"select": "count", "limit": "1"},
        timeout=10
    )
    if r.status_code == 200:
        print(f"✅ Connected to Supabase successfully.")
        print(f"   URL: {cfg['supabase_url']}")
        print(f"   Table: claude_memories — accessible")
    else:
        print(f"❌ Connection failed: {r.status_code} — {r.text}")
        print("   Make sure you've run schema.sql in your Supabase SQL editor.")

# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Claude Memory Helper")
    sub = p.add_subparsers(dest="cmd")

    s_store = sub.add_parser("store")
    s_store.add_argument("--title",    default="")
    s_store.add_argument("--project",  default="")
    s_store.add_argument("--conv-id",  default="")
    s_store.add_argument("--conv-url", default="")

    s_search = sub.add_parser("search")
    s_search.add_argument("--query",   required=True)
    s_search.add_argument("--project", default="")
    s_search.add_argument("--limit",   type=int, default=5)

    s_list = sub.add_parser("list")
    s_list.add_argument("--project", default="")
    s_list.add_argument("--limit",   type=int, default=10)

    s_get = sub.add_parser("get")
    s_get.add_argument("--id", required=True)

    sub.add_parser("setup")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)

    cfg = load_config()

    dispatch = {
        "store":  cmd_store,
        "search": cmd_search,
        "list":   cmd_list,
        "get":    cmd_get,
        "setup":  cmd_setup,
    }
    dispatch[args.cmd](args, cfg)

if __name__ == "__main__":
    main()
