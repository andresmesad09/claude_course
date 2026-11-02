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

See which notes you have, newest first:

```bash
uv run second_brain list
# Notes in /Users/me/second_brain:
# 1. 2026-10-31-091500-another-idea.md
# 2. 2026-10-28-143012-my-brilliant-idea-about-caching.md
```

Only markdown files directly in the notes folder are listed. Hidden files and subfolders are skipped. If there are no notes yet, `list` prints `No notes yet.` and doesn't create the folder.

Print a note to the terminal by its number from `list`:

```bash
uv run second_brain show 2
# # My brilliant idea about caching
#
# My brilliant idea about caching
```

`show` prints only the note's content, so you can pipe it (`second_brain show 2 | pbcopy`). Numbers follow `list`, newest first, so they shift by one whenever you save a new note. A number with no matching note gives a usage error.

Run `second_brain` without a command, or with `--help`, to list the available commands.

Exit codes: `0` means success (the note was saved, listed or shown), `2` means a usage error (such as an empty thought or an unknown note number), and `1` means an unexpected error, in which case the traceback is logged.

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
