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

Run via the CLI entrypoint:

```bash
uv run second_brain
```

Run with the dev environment:

```bash
uv run --env-file .env second_brain
```

Run as a Python module:

```bash
uv run python -m second_brain
```

## Environment Variables

`.env.example` is the template for environment configuration. Copy it to `.env` for development:

```bash
cp .env.example .env
```

| Variable    | Default   | Description                                                      |
|-------------|-----------|------------------------------------------------------------------|
| `LOG_LEVEL` | `INFO`    | Console log level. Set to `DEBUG` in `.env` for verbose output.  |
| `LOG_FILE`  | `app.log` | Path to the log file.                                            |

`.env` is not loaded automatically. Use `uv run --env-file .env` to load the dev environment explicitly.

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
