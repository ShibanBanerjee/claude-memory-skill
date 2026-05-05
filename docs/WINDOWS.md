# Windows Setup Guide

## Important: PowerShell vs Bash Syntax

This skill's setup commands use bash syntax. On Windows, use PowerShell equivalents.

## Creating the Config File

DO NOT use bash heredoc syntax (`cat << 'EOF'`) — it doesn't work in PowerShell.

**Use this instead:**
```powershell
@'
{
  "supabase_url": "https://YOUR_PROJECT_ID.supabase.co",
  "supabase_anon_key": "eyJhbGci..."
}
'@ | Out-File -FilePath "$env:USERPROFILE\.claude_memory_config.json" -Encoding utf8
```

**Verify it worked:**
```powershell
Get-Content "$env:USERPROFILE\.claude_memory_config.json"
```

## Installing Python
Download from [python.org](https://python.org). Make sure to check "Add Python to PATH".

## Installing requests
```powershell
pip install requests
```

## Copying mem.py
```powershell
Copy-Item scripts\mem.py "$env:USERPROFILE\mem.py"
```

## Testing
```powershell
python "$env:USERPROFILE\mem.py" setup
```

## Notes
- The config file lives at `C:\Users\YourName\.claude_memory_config.json`
- When running from Claude sandbox, the skill uses Supabase MCP directly
  (no Windows-side scripts needed for the skill itself)
- `mem.py` on Windows is for manual use and additional control
