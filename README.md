# levels-fyi-mcp

MCP Server for querying compensation data from [levels.fyi](https://levels.fyi). 

## What this server provides

Server name: `LevelsFyi`

Tools:
- `get_recent_offers(company_name: str, role: str, level: str, location: str = None) -> dict` (Hit levels.fyi salary search API to find the recent offer data for given company, role, level, location)
- `get_level_mapping(company_name: str, role: str = "Software Engineer") -> dict` (Get the level mapping for a given job family at a company)

## End User Installation (Use in Cursor)

This section is for users who only want to install and run the MCP server in Cursor.

### Requirements

- Python `>=3.11`
- [uv](https://docs.astral.sh/uv/)

### Cursor MCP configuration (recommended)

Use `uv run` so Cursor uses the project environment directly.

```json
{
  "mcpServers": {
    "user-MyPlayground": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/absolute/path/to/levels-fyi-mcp"
    }
  }
}
```

### Start using it

1. Open Cursor MCP settings and add the server config above.
2. Ensure `cwd` points to your local clone of this repo.
3. Start/reload MCP servers in Cursor.
4. Call tools such as `get_recent_offers`, `get_level_mapping`

### Optional: direct `fastmcp` command

If you prefer `command: "fastmcp"` in Cursor, install it as a global tool:

```bash
uv tool install fastmcp
```

If Cursor cannot find `fastmcp`, use the recommended `uv run` config above.

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

### Tool argument type errors

- `generate_username.add_numbers` must be boolean (`true`/`false`), not numbers or strings.

## Notes

- `get_mock_weather` returns randomized mock data for demos.
- Tool logs are printed from `main.py` and appear in server output.
