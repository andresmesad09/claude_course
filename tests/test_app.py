import os
import re

import pytest
from click.testing import CliRunner
from loguru import logger

from second_brain.app import cli, configure_logging, main, short_level

LOG_LINE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \| INF \| "
    r"\S+:\S+:\d+ \| Hello from the tests!$",
    re.MULTILINE,
)
NOTE_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-my-brilliant-idea\.md$")


@pytest.fixture
def runner():
    return CliRunner()


def test_console_uses_compact_format(capfd):
    configure_logging()
    logger.info("Hello from the tests!")
    captured = capfd.readouterr()
    assert LOG_LINE.search(captured.err)


def test_file_uses_compact_format():
    configure_logging()
    logger.info("Hello from the tests!")
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


def test_new_saves_note_and_prints_path(runner, tmp_path):
    result = runner.invoke(cli, ["new", "My brilliant idea"])
    assert result.exit_code == 0, result.output
    files = list((tmp_path / "notes").iterdir())
    assert len(files) == 1
    assert NOTE_NAME.match(files[0].name)
    assert files[0].read_text(encoding="utf-8") == (
        "# My brilliant idea\n\nMy brilliant idea\n"
    )
    assert f"Saved {files[0]}" in result.output


@pytest.mark.parametrize("text", ["", "   "])
def test_new_rejects_empty_thought(runner, tmp_path, text):
    result = runner.invoke(cli, ["new", text])
    assert result.exit_code == 2
    assert "empty" in result.output.lower()
    assert not (tmp_path / "notes").exists()


def test_new_requires_argument(runner):
    result = runner.invoke(cli, ["new"])
    assert result.exit_code == 2


def test_no_subcommand_shows_help(runner):
    result = runner.invoke(cli, [])
    assert result.exit_code == 2
    assert "Usage:" in result.output
    assert "new" in result.output


def test_main_runs_cli(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.argv", ["second_brain", "new", "from main"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0
    assert len(list((tmp_path / "notes").iterdir())) == 1


def test_main_exits_non_zero_when_save_fails(monkeypatch, tmp_path, capfd):
    not_a_folder = tmp_path / "not_a_folder"
    not_a_folder.touch()
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(not_a_folder))
    monkeypatch.setattr("sys.argv", ["second_brain", "new", "idea"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1
    captured = capfd.readouterr()
    assert "Saved" not in captured.out
    assert "FileExistsError" in captured.err
    assert captured.err.count("Traceback") == 1
    log = (tmp_path / "test.log").read_text()
    assert re.search(r"\| ERR \|", log)


def test_save_is_logged_at_debug(runner, tmp_path):
    result = runner.invoke(cli, ["new", "idea"])
    assert result.exit_code == 0, result.output
    log = (tmp_path / "test.log").read_text()
    assert re.search(r"\| DBG \| .*Saved note ", log)


def test_help_options(runner):
    assert "Usage:" in runner.invoke(cli, ["--help"]).output
    new_help = runner.invoke(cli, ["new", "--help"]).output
    assert "Save TEXT as a new markdown note" in new_help


def test_dotenv_in_cwd_is_loaded(runner, tmp_path, monkeypatch):
    monkeypatch.delenv("SECOND_BRAIN_DIR")
    (tmp_path / ".env").write_text(f"SECOND_BRAIN_DIR={tmp_path / 'from_env'}\n")
    result = runner.invoke(cli, ["new", "idea"])
    assert result.exit_code == 0, result.output
    assert len(list((tmp_path / "from_env").iterdir())) == 1


def test_real_env_wins_over_dotenv(runner, tmp_path):
    (tmp_path / ".env").write_text(f"SECOND_BRAIN_DIR={tmp_path / 'from_env'}\n")
    result = runner.invoke(cli, ["new", "idea"])
    assert result.exit_code == 0, result.output
    assert not (tmp_path / "from_env").exists()
    assert len(list((tmp_path / "notes").iterdir())) == 1


def test_works_without_dotenv(runner, tmp_path):
    assert not (tmp_path / ".env").exists()
    result = runner.invoke(cli, ["new", "idea"])
    assert result.exit_code == 0, result.output


def _make_notes(directory, names):
    directory.mkdir(parents=True, exist_ok=True)
    for name in names:
        (directory / name).write_text("x")


def test_list_shows_path_and_numbered_notes_newest_first(runner, tmp_path):
    notes = tmp_path / "notes"
    _make_notes(
        notes,
        ["2026-10-28-143012-my-brilliant-idea.md", "2026-10-31-091500-another.md"],
    )
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output
    assert result.stdout == (
        f"Notes in {notes.resolve()}:\n"
        "1. 2026-10-31-091500-another.md\n"
        "2. 2026-10-28-143012-my-brilliant-idea.md\n"
    )


def test_list_with_missing_folder(runner, tmp_path):
    notes = tmp_path / "notes"
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output
    assert result.stdout == f"Notes in {notes.resolve()}:\nNo notes yet.\n"
    assert not notes.exists()


def test_list_with_empty_folder(runner, tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output
    assert result.stdout == f"Notes in {notes.resolve()}:\nNo notes yet.\n"


def test_list_shows_absolute_path_for_relative_dir(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("SECOND_BRAIN_DIR", "relative_notes")
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output
    first_line = result.stdout.splitlines()[0]
    assert first_line == f"Notes in {(tmp_path / 'relative_notes').resolve()}:"


def test_new_then_list_round_trip(runner):
    runner.invoke(cli, ["new", "Fresh thought"])
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0, result.output
    assert re.search(
        r"^1\. \d{4}-\d{2}-\d{2}-\d{6}-fresh-thought\.md$",
        result.stdout,
        re.MULTILINE,
    )


def test_list_is_in_help(runner):
    group_help = runner.invoke(cli, ["--help"]).output
    assert re.search(r"^\s+list\s+List saved notes, newest first\.", group_help, re.M)
    list_help = runner.invoke(cli, ["list", "--help"])
    assert list_help.exit_code == 0
    assert "Usage:" in list_help.output


def test_builtin_list_is_not_shadowed():
    import second_brain.app as app

    assert "list" not in vars(app)
