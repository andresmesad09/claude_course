# Usage

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Running

Via the CLI entrypoint:

```bash
uv run second_brain              # show available commands (new, list)
uv run second_brain --help       # same, exits with code 0
uv run second_brain new --help   # help for a single command
uv run second_brain list         # list saved notes, newest first
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

## Listing Notes

```bash
uv run second_brain list
# Notes in /Users/me/second_brain:
# 1. 2026-10-31-091500-another-idea.md
# 2. 2026-10-28-143012-my-brilliant-idea-about-caching.md
```

- **Path:** the first line shows the notes folder as an absolute path, even when `SECOND_BRAIN_DIR` is relative or uses `~`.
- **Order:** newest first, based on the timestamp in each file name, so editing a note doesn't move it.
- **What counts as a note:** only `*.md` files directly in the folder. Hidden files (such as `.DS_Store` or `._note.md`), subfolders and other file types are skipped.
- **No notes:** if the folder is missing or empty, `list` prints `No notes yet.` and exits with code 0. The folder isn't created; that happens on the first `new`.
- **Same-second duplicates:** if the same thought is saved twice within one second, the `-2` copy is listed below the original, because `-` sorts before `.`.

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
