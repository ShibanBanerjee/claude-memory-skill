#!/bin/bash
# claude-memory-skill — Setup Script (Mac / Linux)
# Usage: chmod +x scripts/setup.sh && ./scripts/setup.sh

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     claude-memory-skill  Setup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 1. Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi

# 2. Install requests
echo -e "${YELLOW}[2/5] Installing Python dependencies...${NC}"
pip3 install requests --break-system-packages -q 2>/dev/null || pip3 install requests -q
echo -e "${GREEN}✓ requests library installed${NC}"

# 3. Copy mem.py
echo -e "${YELLOW}[3/5] Installing mem.py...${NC}"
cp mem.py ~/mem.py
chmod +x ~/mem.py
echo -e "${GREEN}✓ mem.py installed to ~/mem.py${NC}"

# 4. Create config if it doesn't exist
echo -e "${YELLOW}[4/5] Checking config file...${NC}"
CONFIG_PATH="$HOME/.claude_memory_config.json"
if [ -f "$CONFIG_PATH" ]; then
    echo -e "${GREEN}✓ Config already exists at $CONFIG_PATH${NC}"
else
    echo ""
    echo "Config file not found. Let's create it."
    echo "You'll need your Supabase project URL and anon key."
    echo "Find them at: Supabase Dashboard → Project Settings → API Keys → Legacy anon key"
    echo ""
    read -p "Supabase project URL (e.g. https://abc123.supabase.co): " SUPABASE_URL
    read -p "Supabase anon key (starts with eyJ...): " SUPABASE_KEY
    
    cat > "$CONFIG_PATH" << EOF
{
  "supabase_url": "$SUPABASE_URL",
  "supabase_anon_key": "$SUPABASE_KEY"
}
EOF
    echo -e "${GREEN}✓ Config created at $CONFIG_PATH${NC}"
fi

# 5. Install SKILL.md
echo -e "${YELLOW}[5/5] Installing Claude skill...${NC}"
SKILL_DIR="/mnt/skills/user/claude-memory"
if [ -d "/mnt/skills/user" ]; then
    mkdir -p "$SKILL_DIR"
    cp SKILL.md "$SKILL_DIR/SKILL.md"
    echo -e "${GREEN}✓ SKILL.md installed to $SKILL_DIR${NC}"
else
    echo -e "${YELLOW}⚠ Claude skills directory not found at /mnt/skills/user${NC}"
    echo "  Copy SKILL.md manually to your Claude skills directory."
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Run schema.sql in your Supabase SQL Editor to create the database table"
echo "     (Supabase Dashboard → SQL Editor → paste schema.sql → Run)"
echo ""
echo "  2. Test your connection:"
echo "     python3 ~/mem.py setup"
echo ""
echo "  3. In any Claude conversation, type:"
echo "     /mem      → save conversation to memory"
echo "     /context  → restore memory in future sessions"
echo ""
echo -e "${GREEN}Setup complete. See docs/ for full documentation.${NC}"
echo ""
