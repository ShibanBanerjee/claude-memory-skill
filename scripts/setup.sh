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
echo -e "${YELLOW}[1/3] Checking Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi

# 2. Install mem.py
echo -e "${YELLOW}[2/3] Installing mem.py...${NC}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MEM_SRC="$SCRIPT_DIR/mem.py"
[ -f "$MEM_SRC" ] || MEM_SRC="$SCRIPT_DIR/../mem.py"
[ -f "$MEM_SRC" ] || MEM_SRC="mem.py"
cp "$MEM_SRC" ~/mem.py
chmod +x ~/mem.py
python3 ~/mem.py setup
echo -e "${GREEN}✓ mem.py installed and database initialised${NC}"

# 3. Install SKILL.md
echo -e "${YELLOW}[3/3] Installing Claude skill...${NC}"
SKILL_DIR="$HOME/.claude/skills/claude-memory"
mkdir -p "$SKILL_DIR"
SKILL_SRC="$SCRIPT_DIR/../SKILL.md"
[ -f "$SKILL_SRC" ] || SKILL_SRC="SKILL.md"
cp "$SKILL_SRC" "$SKILL_DIR/SKILL.md"
echo -e "${GREEN}✓ SKILL.md installed to $SKILL_DIR${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo "Setup complete. In any Claude conversation, type:"
echo ""
echo "  /mem      → save conversation to memory"
echo "  /context  → restore memory in future sessions"
echo ""
echo -e "${GREEN}No further configuration required.${NC}"
echo ""
