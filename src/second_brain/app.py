import sys
from datetime import datetime

import click
from dotenv import find_dotenv, load_dotenv
from loguru import logger

from second_brain.notes import notes_dir, save_note

LEVEL_ABBREVIATIONS = {
    "TRACE": "TRC",
    "DEBUG": "DBG",
    "INFO": "INF",
    "SUCCESS": "SUC",
    "WARNING": "WRN",
    "ERROR": "ERR",
    "CRITICAL": "CRT",
}

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{extra[lvl]}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def short_level(name):
    """Return the 3-letter abbreviation for a log level name.

    Unknown (custom) levels fall back to their first 3 characters, uppercased.
    """
    return LEVEL_ABBREVIATIONS.get(name, name[:3].upper())


def _add_short_level(record):
    record["extra"]["lvl"] = short_level(record["level"].name)


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
    - File handler at DEBUG level writing to LOG_FILE (default: app.log)

    Both handlers use the compact LOG_FORMAT, e.g.
    ``2026-10-26 14:03:12 | DBG | second_brain.app:new:77 | Saved note ...``.
    """
    import os

    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = os.environ.get("LOG_FILE", "app.log")
    logger.remove()
    logger.configure(patcher=_add_short_level)
    logger.add(sys.stderr, level=log_level, format=LOG_FORMAT)
    logger.add(
        log_file, level="DEBUG", format=LOG_FORMAT, rotation="50 KB", retention=1
    )


@click.group()
def cli():
    """Second brain: capture quick thoughts as markdown."""
    load_dotenv(find_dotenv(usecwd=True))
    configure_logging()


@cli.command()
@click.argument("text")
def new(text):
    """Save TEXT as a new markdown note."""
    try:
        path = save_note(text, notes_dir(), datetime.now())
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    logger.debug("Saved note {}", path)
    click.echo(f"Saved {path}")


def _exit_with_error(_exc):
    sys.exit(1)


@logger.catch(onerror=_exit_with_error)
def main():
    """Run the CLI, logging any unexpected exception with a traceback.

    After logging, exits with code 1 so callers can tell the run failed.
    """
    cli()


if __name__ == "__main__":
    main()
