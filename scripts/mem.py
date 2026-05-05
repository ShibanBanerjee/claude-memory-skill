#!/usr/bin/env python3
"""
Claude Memory Skill — mem.py v1.2.0
Local CLI helper for storing and retrieving Claude memories via Supabase REST API.

Usage:
  python3 mem.py setup                    Test connection
  python3 mem.py store --title "..." --project "..."   Store (reads JSON from stdin)
  python3 mem.py search --query "..."     Full-text search
  python3 mem.py list [--project "..."]   List recent memories
  python3 mem.py get --id "uuid"          Get single memory by ID
  python3 mem.py delete --id "uuid"       Delete a memory

Config file: ~/.claude_memory_config.json
  { "supabase_url": "...", "supabase_anon_key": "..." }
"""

import sys, os, json, re, argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed.")
    print("Run: pip install requests --break-system-packages")
    sys.exit(1)

CONFIG_PATH = Path.home() / ".claude_memory_config.json"
VERSION = "1.2.0"

# ── Config ────────────────────────────────────────────────────────────────────
def load_config():
    if not CONFIG_PATH.exists():
        print(f"""
ERROR: Config file not found.

Create it at: {CONFIG_PATH}
{{
  "supabase_url": "https://YOUR_PROJECT.supabase.co",
  "supabase_anon_key": "eyJhbGci..."
}}

Get your legacy anon key from:
Supabase Dashboard → Settings → API Keys → Legacy anon tab
""")
        sys.exit(1)
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file: {e}")
        sys.exit(1)

def headers(cfg):
    key = cfg["supabase_anon_key"]
    h = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if not key.startswith("sb_"):
        h["apikey"] = key
    return h

def base_url(cfg):
    return cfg["supabase_url"].rstrip("/") + "/rest/v1"

# ── Setup ─────────────────────────────────────────────────────────────────────
def cmd_setup(args, cfg):
    print(f"Claude Memory Skill v{VERSION}")
    print(f"Config: {CONFIG_PATH}")
    print(f"URL: {cfg['supabase_url']}")
    print("Testing connection...")
    try:
        r = requests.get(
            f"{base_url(cfg)}/claude_memories",
            headers=headers(cfg),
            params={"select": "count", "limit": "1"},
            timeout=10
        )
        if r.status_code == 200:
            count_r = requests.get(
                f"{base_url(cfg)}/claude_memories",
                headers={**headers(cfg), "Prefer": "count=exact"},
                params={"select": "id"},
                timeout=10
            )
            total = count_r.headers.get("content-range", "?/?").split("/")[-1]
            print(f"Connected to Supabase successfully.")
            print(f"Table: claude_memories — {total} memories stored.")
        else:
            print(f"Connection failed: {r.status_code} — {r.text}")
            print("Make sure you have run scripts/schema.sql in your Supabase SQL editor.")
    except requests.exceptions.ConnectionError:
        print("Connection error — check your Supabase URL.")
    except requests.exceptions.Timeout:
        print("Connection timed out — check your internet connection.")

# ── Store ─────────────────────────────────────────────────────────────────────
def cmd_store(args, cfg):
    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: No JSON received on stdin.")
        print("Usage: echo '{...}' | python3 mem.py store --title '...'")
        sys.exit(1)
    try:
        memory = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        sys.exit(1)

    if args.title:   memory["title"]   = args.title
    if args.project: memory["project"] = args.project
    if args.conv_url:memory["conversation_url"] = args.conv_url

    for field in ["title", "summary"]:
        if not memory.get(field):
            print(f"ERROR: Memory must include '{field}' field.")
            sys.exit(1)

    memory["token_count_est"] = len(memory.get("summary", "").split())

    r = requests.post(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        json=memory,
        timeout=20
    )
    if r.status_code not in (200, 201):
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    result = r.json()
    if isinstance(result, list): result = result[0]
    decisions = len(memory.get("key_decisions", []))
    questions = len(memory.get("open_questions", []))
    words = memory["token_count_est"]

    print(f"""
Memory saved successfully.

  ID:        {result.get('id')}
  Title:     {result.get('title')}
  Project:   {memory.get('project', 'unset')}
  Summary:   ~{words} words
  Decisions: {decisions}
  Questions: {questions}
  Saved at:  {result.get('created_at', '')[:19]}

Use /context {memory.get('project', memory.get('title', ''))} to restore in any future session.
""")

# ── Search ────────────────────────────────────────────────────────────────────
def cmd_search(args, cfg):
    if not args.query:
        print("ERROR: --query required")
        sys.exit(1)

    ts_query = " & ".join(re.sub(r'[^\w\s]', '', args.query).split())
    params = {
        "select": "id,created_at,title,project,tags,summary,key_decisions,open_questions,conversation_url",
        "search_vector": f"fts.{ts_query}",
        "order": "created_at.desc",
        "limit": str(args.limit or 5),
    }
    if args.project:
        params["project"] = f"ilike.*{args.project}*"

    r = requests.get(f"{base_url(cfg)}/claude_memories", headers=headers(cfg), params=params, timeout=15)
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    results = r.json()
    if not results:
        print(f"No memories found for: '{args.query}'")
        print("Try broader search terms or use: python3 mem.py list")
        return

    print(f"\nFound {len(results)} memory/memories for '{args.query}':\n")
    for m in results:
        print(f"  [{m['id'][:8]}...]  {m['title']}")
        print(f"  Project: {m.get('project','—')}  |  Date: {m['created_at'][:10]}")
        print(f"  Tags: {', '.join(m.get('tags', []))}")
        print(f"  Decisions: {len(m.get('key_decisions',[]))}  |  Questions: {len(m.get('open_questions',[]))}")
        print(f"  Preview: {m['summary'][:200]}...")
        if m.get('conversation_url'):
            print(f"  Link: {m['conversation_url']}")
        print()

    if args.json:
        print("\n--- JSON ---")
        print(json.dumps(results, indent=2))

# ── List ──────────────────────────────────────────────────────────────────────
def cmd_list(args, cfg):
    params = {
        "select": "id,created_at,title,project,tags,token_count_est",
        "order": "created_at.desc",
        "limit": str(args.limit or 20),
    }
    if args.project:
        params["project"] = f"ilike.*{args.project}*"

    r = requests.get(f"{base_url(cfg)}/claude_memories", headers=headers(cfg), params=params, timeout=15)
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text}")
        sys.exit(1)

    results = r.json()
    if not results:
        print("No memories stored yet. Use /mem to save your first memory.")
        return

    print(f"\n{'Date':<12} {'ID':<12} {'Project':<15} {'Title':<45} {'Words'}")
    print("-" * 95)
    for m in results:
        date = m['created_at'][:10]
        mid  = m['id'][:8] + "..."
        proj = (m.get('project') or '—')[:14]
        title= m['title'][:44]
        words= str(m.get('token_count_est') or '—')
        print(f"{date:<12} {mid:<12} {proj:<15} {title:<45} {words}")
    print()

# ── Get ───────────────────────────────────────────────────────────────────────
def cmd_get(args, cfg):
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
        print(f"No memory found with ID: {args.id}")
        return
    print(json.dumps(results[0], indent=2))

# ── Delete ────────────────────────────────────────────────────────────────────
def cmd_delete(args, cfg):
    confirm = input(f"Delete memory {args.id}? This cannot be undone. Type 'yes' to confirm: ")
    if confirm.strip().lower() != 'yes':
        print("Cancelled.")
        return
    r = requests.delete(
        f"{base_url(cfg)}/claude_memories",
        headers=headers(cfg),
        params={"id": f"eq.{args.id}"},
        timeout=15
    )
    if r.status_code in (200, 204):
        print(f"Memory {args.id} deleted.")
    else:
        print(f"ERROR {r.status_code}: {r.text}")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description=f"Claude Memory Skill CLI v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 mem.py setup
  python3 mem.py list
  python3 mem.py search --query "my-project brainstorm"
  python3 mem.py get --id "e1ccaea5-7cb2-4893-871b-cc83846e5c3e"
  echo '{"title":"Test","summary":"..."}' | python3 mem.py store --project "MyProject"
        """
    )
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("setup", help="Test Supabase connection")

    s = sub.add_parser("store", help="Store memory from stdin JSON")
    s.add_argument("--title",    default="", help="Override title")
    s.add_argument("--project",  default="", help="Override project")
    s.add_argument("--conv-url", default="", help="Conversation URL")

    s = sub.add_parser("search", help="Full-text search memories")
    s.add_argument("--query",   required=True)
    s.add_argument("--project", default="")
    s.add_argument("--limit",   type=int, default=5)
    s.add_argument("--json",    action="store_true", help="Also output raw JSON")

    s = sub.add_parser("list", help="List recent memories")
    s.add_argument("--project", default="")
    s.add_argument("--limit",   type=int, default=20)

    s = sub.add_parser("get", help="Get full memory by ID")
    s.add_argument("--id", required=True)

    s = sub.add_parser("delete", help="Delete a memory by ID")
    s.add_argument("--id", required=True)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(0)

    cfg = load_config()
    {"setup": cmd_setup, "store": cmd_store, "search": cmd_search,
     "list": cmd_list, "get": cmd_get, "delete": cmd_delete}[args.cmd](args, cfg)

if __name__ == "__main__":
    main()
