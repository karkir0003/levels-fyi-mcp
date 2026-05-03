# levels-fyi-mcp

MCP Server for querying compensation data from [levels.fyi](https://levels.fyi). 

## What this server provides

Server name: `LevelsFyi`

Tools:
- `get_recent_offers(company_name: str, role: str, level: str, location: str = None) -> dict` (Hit levels.fyi salary search API to find the recent offer data for given company, role, level, location)
- `get_level_mapping(company_name: str, role: str = "Software Engineer") -> dict` (Get the level mapping for a given job family at a company)

## End User Installation

This section is for users who only want to install and run the MCP server in Cursor.

### Requirements

- Python `>=3.11`
- [uv](https://docs.astral.sh/uv/)

### Installing the MCP
This MCP is hosted on [Prefect Horizon](https://horizon.prefect.io), which is a low-code/no-code way to host MCP servers for LLMs to be able to use. The MCP URL is `https://levels-fyi.fastmcp.app/mcp`, so you should be able to use this server address to add to Codex, Claude Code, OpenAI SDK, Cursor, Gemini CLI. 

For example, in Claude Code, you can reference this [wiki](https://code.claude.com/docs/en/mcp) for how to install the MCP server. You can run `claude mcp add --transport http levels-mcp https://levels-fyi.fastmcp.app/mcp` to install the MCP server.

If you're on Cursor, you can visit this [link](cursor://anysphere.cursor-deeplink/mcp/install?name=levels-fyi&config=eyJ1cmwiOiJodHRwczovL2xldmVscy1meWkuZmFzdG1jcC5hcHAvbWNwIn0%3D) and follow the on-screen instructions

## Developer Setup

This section is for contributors working on code changes.

### Install dependencies

From the project root:

```bash
uv sync
```

### Run server locally

```bash
uv run python main.py
```

### Add or update dependencies

```bash
uv add <package>
uv sync
```

### Quick environment check

```bash
uv run python -c "import fastmcp; print('fastmcp ok')"
```

## Project structure

```text
.
├── main.py
├── src/
├── pyproject.toml
└── README.md
```

## Troubleshooting

### Failed to spawn: fastmcp (os error 2)

Cause: Cursor cannot find the `fastmcp` executable.

Fix:
1. Prefer Cursor config with `uv run python main.py`, or
2. Install global tool with `uv tool install fastmcp` and ensure PATH includes the uv tool bin (commonly `~/.local/bin`).
