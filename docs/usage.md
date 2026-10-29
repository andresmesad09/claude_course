# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run second_brain             # list available commands
uv run second_brain --help      # same, exits with code 0
uv run second_brain new --help  # help for a single command
```

Or as a Python module:

```bash
uv run python -m second_brain new "My idea"
```

Running `second_brain` with no command prints the help and exits with code 2. This is Click's default behavior for command groups.

## Saving a Note

```bash
uv run second_brain new "My brilliant idea about caching"
# Saved /Users/me/second_brain/2026-10-28-143012-my-brilliant-idea-about-caching.md
```

- **Location:** `SECOND_BRAIN_DIR`, or `~/second_brain/` by default. The folder is created if needed.
- **File name:** `YYYY-MM-DD-HHMMSS-<slug>.md`. The slug is the lowercased thought, with each run of non-alphanumeric characters replaced by `-`, capped at 50 characters. If the thought has no letters or digits, only the timestamp is used.
- **No overwrites:** if the name is already taken, a `-2`, `-3`, … suffix is added.
- **Content:** the first line as an H1 heading, a blank line, then the full text:

  ```markdown
  # My brilliant idea about caching

  My brilliant idea about caching
  ```

- **Empty thoughts:** an empty or whitespace-only thought is rejected with a usage error (exit code 2), and no file is created.
- **Errors:** if a note can't be saved, for example because `SECOND_BRAIN_DIR` points to a file, the traceback is logged and the command exits with code 1.

## Environment Variables

| Variable           | Default          | Description                                   |
|--------------------|------------------|-----------------------------------------------|
| `SECOND_BRAIN_DIR` | `~/second_brain` | Folder notes are saved in (`~` is expanded)   |
| `LOG_LEVEL`        | `INFO`           | Console log level (DEBUG, INFO, …)            |
| `LOG_FILE`         | `app.log`        | Path to the log file                          |

`.env` is loaded automatically from the current working directory. Variables that are already set in your environment take priority over `.env`. Copy `.env.example` to `.env` for development defaults.

## Log Format

Console and file logs share a compact format, with no milliseconds and 3-letter level names:

```
2026-10-26 14:03:12 | DBG | second_brain.app:new:77 | Saved note /Users/me/second_brain/2026-10-26-140312-idea.md
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
