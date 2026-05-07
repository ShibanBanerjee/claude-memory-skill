#!/bin/bash
# claude-memory-skill — Setup Script (Mac / Linux)
# Usage: chmod +x scripts/setup.sh && ./scripts/setup.sh

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     claude-memory-skill  Setup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 1. Check Python
echo -e "${YELLOW}[1/4] Checking Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi

# 2. Check / install requests
echo -e "${YELLOW}[2/4] Checking requests library...${NC}"
if python3 -c "import requests" 2>/dev/null; then
    echo -e "${GREEN}✓ requests already installed${NC}"
else
    echo "Installing requests..."
    pip install requests
    echo -e "${GREEN}✓ requests installed${NC}"
fi

# 3. Install mem.py
echo -e "${YELLOW}[3/4] Installing mem.py...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEM_SRC="$SCRIPT_DIR/mem.py"
[ -f "$MEM_SRC" ] || MEM_SRC="$SCRIPT_DIR/../mem.py"
[ -f "$MEM_SRC" ] || MEM_SRC="mem.py"
cp "$MEM_SRC" ~/mem.py
chmod +x ~/mem.py
echo -e "${GREEN}✓ mem.py installed to ~/mem.py${NC}"

# 4. Check credentials and test connection
echo -e "${YELLOW}[4/4] Checking Supabase credentials...${NC}"
CONFIG="$HOME/.claude_memory_config.json"
if [ ! -f "$CONFIG" ]; then
    echo ""
    echo "  ~/.claude_memory_config.json not found."
    echo "  Create it with your Supabase project credentials:"
    echo ""
    echo '  {
    "supabase_url": "https://your-project.supabase.co",
    "supabase_anon_key": "your-anon-key"
  }'
    echo ""
    echo "  Your URL and anon key are at: Supabase Dashboard → Project Settings → API"
    echo ""
    echo -e "${YELLOW}  Skipping connection test — create the config file and run: python3 ~/mem.py setup${NC}"
else
    python3 ~/mem.py setup
    echo -e "${GREEN}✓ Supabase connection verified${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo "Next step: install the skill in Claude"
echo ""
echo "  Claude Desktop / Claude.ai:"
echo "    Settings → Skills → Add Custom Skill → upload SKILL.md"
echo ""
echo "  Claude Code:"
SKILL_SRC="$SCRIPT_DIR/../SKILL.md"
echo "    mkdir -p ~/.claude/skills/claude-memory"
echo "    cp $SKILL_SRC ~/.claude/skills/claude-memory/SKILL.md"
echo ""
echo "Then in any Claude conversation, type:"
echo "  /mem      → save conversation to memory"
echo "  /context  → restore memory in future sessions"
echo ""
