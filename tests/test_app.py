import os
import re

import pytest
from loguru import logger

from second_brain.app import configure_logging, main, short_level

LOG_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| "
    r"second_brain\.app:main:\d+ \| Hello from second_brain!$",
    re.MULTILINE,
)


def test_main_logs_greeting(capfd):
    main()
    captured = capfd.readouterr()
    assert "Hello from second_brain!" in captured.err


def test_console_uses_compact_format(capfd):
    main()
    captured = capfd.readouterr()
    assert LOG_LINE.search(captured.err)


def test_file_uses_compact_format(capfd):
    main()
    with open(os.environ["LOG_FILE"]) as f:
        content = f.read()
    assert LOG_LINE.search(content)
    assert "<green>" not in content


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("TRACE", "TRC"),
        ("DEBUG", "DBG"),
        ("INFO", "INF"),
        ("SUCCESS", "SUC"),
        ("WARNING", "WRN"),
        ("ERROR", "ERR"),
        ("CRITICAL", "CRT"),
        ("notice", "NOT"),
    ],
)
def test_short_level(name, expected):
    assert short_level(name) == expected


def test_exceptions_still_show_traceback(capfd):
    @logger.catch
    def boom():
        raise RuntimeError("kaboom")

    configure_logging()
    boom()
    captured = capfd.readouterr()
    assert "Traceback" in captured.err
    assert "RuntimeError: kaboom" in captured.err
    assert re.search(r"\| ERR \|", captured.err)
