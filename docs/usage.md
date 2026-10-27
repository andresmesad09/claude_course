# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run second_brain                          # production defaults
uv run --env-file .env second_brain          # dev settings
```

Or as a Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

| Variable    | Default    | Description                          |
|-------------|------------|--------------------------------------|
| `LOG_LEVEL` | `INFO`     | Console log level (DEBUG, INFO, …)   |
| `LOG_FILE`  | `app.log`  | Path to the log file                 |

Copy `.env.example` to `.env` for development defaults, then run with `uv run --env-file .env`.

## Log Format

Console and file logs share a compact format, with no milliseconds and 3-letter level names:

```
2026-10-26 14:03:12 | INF | second_brain.app:main:29 | Hello from second_brain!
```

| Level    | Short |
|----------|-------|
| TRACE    | `TRC` |
| DEBUG    | `DBG` |
| INFO     | `INF` |
| SUCCESS  | `SUC` |
| WARNING  | `WRN` |
| ERROR    | `ERR` |
| CRITICAL | `CRT` |

Custom levels use the first 3 characters of their name, uppercased.
