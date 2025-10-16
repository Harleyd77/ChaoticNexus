# ChaoticNexus - MCP Servers Setup Guide

## 🔌 What are MCP Servers?

MCP (Model Context Protocol) servers are tools that extend Cursor/Claude's capabilities:
- File system access
- Database connections
- Browser automation (Playwright)
- API integrations
- Custom tools

## 📍 Where MCP Configurations Live

### Cursor MCP Configuration:
**Location:** 
- Windows: `C:\Users\YourName\AppData\Roaming\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Linux: `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Important:** These are **global Cursor settings**, not project-specific!

## 🔄 Setting Up MCP Servers Across Computers

### Option 1: Manual Setup (Each Computer)

You need to configure MCP servers on each computer individually because:
- Paths are different on each machine
- MCP config is in Cursor's global settings
- Not part of the Git repository

### Option 2: Shared Configuration Template

Create a template in your project that you can reference:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/ChaoticNexus"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@localhost/chaoticnexus"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@executeautomation/playwright-mcp-server"
      ]
    }
  }
}
```

## 📋 Recommended MCP Servers for ChaoticNexus

### 1. Filesystem Server (Essential)
**Purpose:** Let AI read/write project files

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/path/to/ChaoticNexus"
  ]
}
```

**Update path for each computer:**
- Windows WSL: `/mnt/c/Users/user/Documents/GitHub/ChaoticNexus`
- Ubuntu: `/home/username/Documents/GitHub/ChaoticNexus`
- Mac: `/Users/username/Documents/GitHub/ChaoticNexus`
- Windows: `C:\\Users\\user\\Documents\\GitHub\\ChaoticNexus`

### 2. PostgreSQL Server (Optional - for production)
**Purpose:** Database access for AI to query/modify

```json
"postgres": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-postgres",
    "postgresql://appuser:password@localhost/chaoticnexus"
  ]
}
```

### 3. Playwright/Browser Server (Optional - for testing)
**Purpose:** Browser automation for testing

```json
"playwright": {
  "command": "npx",
  "args": [
    "-y",
    "@executeautomation/playwright-mcp-server"
  ]
}
```

### 4. SQLite Server (Recommended for dev)
**Purpose:** Access to local SQLite database

```json
"sqlite": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-sqlite",
    "/path/to/ChaoticNexus/storage/dev.db"
  ]
}
```

## 🚀 Setup Instructions Per Computer

### Windows WSL (This PC):

1. Open Cursor settings (Ctrl+Shift+P → "Preferences: Open User Settings (JSON)")
2. Or manually edit: `C:\Users\user\AppData\Roaming\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
3. Add MCP servers with WSL paths:

```json
{
  "mcpServers": {
    "chaoticnexus-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/mnt/c/Users/user/Documents/GitHub/ChaoticNexus"
      ]
    },
    "chaoticnexus-sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/mnt/c/Users/user/Documents/GitHub/ChaoticNexus/storage/dev.db"
      ]
    }
  }
}
```

### Ubuntu Production:

```json
{
  "mcpServers": {
    "chaoticnexus-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/username/Documents/GitHub/ChaoticNexus"
      ]
    },
    "chaoticnexus-sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/home/username/Documents/GitHub/ChaoticNexus/storage/production.db"
      ]
    }
  }
}
```

### Other Dev Computers:

Just update the paths to match where you cloned ChaoticNexus.

## 📝 Creating a Project MCP Template

Store this in your project for reference:

```bash
# Create MCP config template
cat > mcp_config_template.json << 'MCPEOF'
{
  "_comment": "MCP Server Configuration Template for ChaoticNexus",
  "_instructions": "Copy this to your Cursor MCP settings and update paths",
  "_location_windows": "C:\\Users\\YourName\\AppData\\Roaming\\Cursor\\User\\globalStorage\\saoudrizwan.claude-dev\\settings\\cline_mcp_settings.json",
  "_location_mac": "~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
  "_location_linux": "~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
  
  "mcpServers": {
    "chaoticnexus-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "UPDATE_THIS_PATH_TO_YOUR_CHAOTICNEXUS_FOLDER"
      ]
    },
    "chaoticnexus-sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "UPDATE_THIS_PATH_TO_YOUR_CHAOTICNEXUS_FOLDER/storage/dev.db"
      ]
    }
  }
}
MCPEOF
```

## 🔐 What Gets Synced vs. What Doesn't

### ✅ Can Be Synced via Git:
- MCP config template (as reference)
- Documentation about MCP setup
- Scripts that use MCP

### ❌ NOT Synced (Computer-Specific):
- Actual MCP configuration in Cursor
- File paths (different per computer)
- Database connection strings
- API keys (if any)

## 🎯 Best Practices

### 1. Use Project-Specific Names
```json
"chaoticnexus-fs": { ... }    // ✅ Good
"filesystem": { ... }          // ❌ Conflicts with other projects
```

### 2. Document Your MCP Setup
Keep `mcp_config_template.json` in the repo with instructions.

### 3. Environment-Specific Configs
Different configs for production vs. development:
- Dev: Point to `storage/dev.db`
- Production: Point to `storage/production.db` or PostgreSQL

### 4. Test MCP Servers
After setup, test in Cursor:
```
Ask Claude: "Can you list the files in this project?"
```

## 🆘 Troubleshooting

### MCP Server Not Working
1. Check if npx is installed: `npx --version`
2. Check Cursor's MCP settings location
3. Verify paths are correct
4. Restart Cursor

### "Command not found: npx"
Install Node.js: https://nodejs.org/

### Database Connection Errors
- Check database file exists
- Verify permissions
- Test connection string

### Path Issues on Windows
Use forward slashes or escaped backslashes:
- ✅ `C:\\Users\\user\\path` 
- ✅ `/mnt/c/Users/user/path` (WSL)
- ❌ `C:\Users\user\path`

## 📚 Resources

- MCP Protocol: https://modelcontextprotocol.io/
- Available MCP Servers: https://github.com/modelcontextprotocol/servers
- Cursor MCP Docs: Check Cursor documentation

## 💡 Pro Tips

1. **Keep a cheatsheet:** Save your MCP config in the project for reference
2. **Use relative paths when possible:** Makes configs more portable
3. **Version control the template:** Everyone gets same starting point
4. **Document required servers:** In README or project docs

---

**Remember:** MCP configs are global to Cursor, not per-project!  
You need to set them up on each computer, but the template helps. 🔌
