# MCP Configuration for Cortex Core

To expose cortex-core tools via MCP in Cursor, add this configuration:

## Option 1: Cursor UI Configuration

1. Open **Cursor Settings** → **Features** → **MCP**
2. Click **"Add New MCP Server"**
3. Configure:
   - **Name**: `cortex-core`
   - **Type**: `stdio`
   - **Command**: `python3 ~/cortex-core/mcp_server.py`
     (Replace `~/cortex-core` with your actual clone path, e.g. `$HOME/cortex-core`)

## Option 2: JSON Configuration File

If Cursor uses a JSON config file (typically at `~/.cursor/mcp.json` or similar), add:

```json
{
  "mcpServers": {
    "cortex-core": {
      "command": "python3",
      "args": ["/path/to/cortex-core/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Note**: Replace `/path/to/cortex-core` with your actual clone path (e.g. `$HOME/cortex-core` or `~/cortex-core`; some hosts expand `~`, others need an absolute path).

## What This Exposes

Once configured, all tools from `config/tool_catalog.json` will be available as MCP tools, including:

- `cortex_list_models` - **List models from catalog (SSoT)** — filter by provider, capability, modality; get summary/full/codes
- `cortex_add_to_catalog` - **Add new models/tools**
- `tavily_search` - Web search
- `perplexity_search` - Research search
- `google_programmable_search` - Google search
- `anthropic_computer_use` - GUI automation
- `anthropic_bash` - Shell commands
- `anthropic_text_editor` - File editing
- And all other tools in your catalog

## Usage

After configuration, external AIs can:
1. Discover available tools via `tools/list`
2. Call tools via `tools/call` with tool name and arguments
3. Add new models/tools using `cortex_add_to_catalog`

## Testing

Test the MCP server directly:
```bash
echo '{"method":"tools/list"}' | python3 mcp_server.py
```
