# aivengers-mcp MCP server

Dynamically search and call tools in AIvengers

## Components

### Tools

The server implements 2 tools:
- search-actions: Intent based search for dynamic actions
- call-action: Calls a dynamic action

## Configuration

Requires `AGIVERSE_API_KEY` environment variable to be set.

You can get your API key for free at [AGIverse](https://app.agiverse.io/).

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
"mcpServers": {
  "aivengers-mcp": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/agiverse/aivengers-mcp",
      "aivengers-mcp"
    ],
    "env": {
      "AGIVERSE_API_KEY": ""
    }
  }
}
```
