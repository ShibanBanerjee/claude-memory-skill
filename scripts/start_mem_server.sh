#!/bin/bash
# start_mem_server.sh
# Starts the Claude Memory Server in the background on Mac/Linux.
# Mac users can also set up a launchd agent for auto-start on login.

SERVER_SCRIPT="$HOME/mem_server.py"
PORT=7823

# Download if not present
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "Downloading mem_server.py..."
    curl -o "$SERVER_SCRIPT" https://raw.githubusercontent.com/ShibanBanerjee/claude-memory-skill/main/mem_server.py
    echo "Downloaded to $SERVER_SCRIPT"
fi

# Check if already running
if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
    echo "Claude Memory Server is already running on port $PORT"
    exit 0
fi

# Start in background
nohup python3 "$SERVER_SCRIPT" > "$HOME/.claude_memory_server.log" 2>&1 &
PID=$!

sleep 1

if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
    echo ""
    echo "✅ Claude Memory Server started"
    echo "   PID    : $PID"
    echo "   Health : http://localhost:$PORT/health"
    echo "   Log    : $HOME/.claude_memory_server.log"
    echo ""
else
    echo "❌ Server failed to start. Check log: $HOME/.claude_memory_server.log"
    exit 1
fi

# Mac auto-start instructions
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "To auto-start on login (Mac), create a launchd agent:"
    echo ""
    echo "  cat > ~/Library/LaunchAgents/com.claude.memory.plist << 'EOF'"
    echo "  <?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    echo "  <!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">"
    echo "  <plist version=\"1.0\">"
    echo "  <dict>"
    echo "    <key>Label</key><string>com.claude.memory</string>"
    echo "    <key>ProgramArguments</key>"
    echo "    <array><string>$(which python3)</string><string>$SERVER_SCRIPT</string></array>"
    echo "    <key>RunAtLoad</key><true/>"
    echo "    <key>KeepAlive</key><true/>"
    echo "  </dict>"
    echo "  </plist>"
    echo "  EOF"
    echo "  launchctl load ~/Library/LaunchAgents/com.claude.memory.plist"
fi

# Linux auto-start instructions
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "To auto-start on login (Linux systemd user service):"
    echo ""
    echo "  mkdir -p ~/.config/systemd/user"
    echo "  cat > ~/.config/systemd/user/claude-memory.service << 'EOF'"
    echo "  [Unit]"
    echo "  Description=Claude Memory Server"
    echo "  After=network.target"
    echo ""
    echo "  [Service]"
    echo "  ExecStart=$(which python3) $SERVER_SCRIPT"
    echo "  Restart=always"
    echo ""
    echo "  [Install]"
    echo "  WantedBy=default.target"
    echo "  EOF"
    echo "  systemctl --user enable claude-memory"
    echo "  systemctl --user start claude-memory"
fi
