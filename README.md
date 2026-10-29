# second-brain

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd second-brain
   ```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

## Usage

Save a quick thought as a markdown note:

```bash
uv run second_brain new "My brilliant idea about caching"
# Saved /Users/me/second_brain/2026-10-28-143012-my-brilliant-idea-about-caching.md
```

Each note is a plain markdown file named `YYYY-MM-DD-HHMMSS-<slug>.md`. It contains the first line of the thought as a heading, followed by the full text. Existing notes are never overwritten: a name that's already taken gets a `-2`, `-3`, … suffix.

Run `second_brain` without a command, or with `--help`, to list the available commands.

Run as a Python module:

```bash
uv run python -m second_brain new "Another idea"
```

## Environment Variables

`.env.example` is the template for environment configuration. Copy it to `.env` for development:

```bash
cp .env.example .env
```

| Variable           | Default          | Description                                                      |
|--------------------|------------------|------------------------------------------------------------------|
| `SECOND_BRAIN_DIR` | `~/second_brain` | Folder notes are saved in. `~` is expanded, and missing folders are created. |
| `LOG_LEVEL`        | `INFO`           | Console log level. Set to `DEBUG` in `.env` for verbose output.  |
| `LOG_FILE`         | `app.log`        | Path to the log file.                                            |

`.env` is loaded automatically from the current working directory. Variables that are already set in your shell take priority over values in `.env`.

### Log format

Console and file logs share a compact format, with no milliseconds and 3-letter levels (`TRC`, `DBG`, `INF`, `SUC`, `WRN`, `ERR`, `CRT`):

```
2026-10-26 14:03:12 | DBG | second_brain.app:new:77 | Saved note /Users/me/second_brain/2026-10-26-140312-idea.md
```

## Testing

Run the tests:

```bash
uv run pytest
```

Run the tests with coverage:

```bash
uv run pytest --cov
```

## Documentation

Preview the docs locally:

```bash
uv run python scripts/serve_docs.py
```

Build static docs:

```bash
uv run mkdocs build
```
