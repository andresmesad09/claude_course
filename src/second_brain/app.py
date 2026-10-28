import sys

from loguru import logger

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
    ``2026-10-26 14:03:12 | INF | second_brain.app:main:29 | Hello``.
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


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from second_brain!")


if __name__ == "__main__":
    main()
