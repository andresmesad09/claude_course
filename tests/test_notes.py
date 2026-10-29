from datetime import datetime
from pathlib import Path

import pytest

from second_brain.notes import (
    DEFAULT_DIR_NAME,
    note_filename,
    notes_dir,
    render_note,
    save_note,
    slugify,
)

NOW = datetime(2026, 10, 28, 14, 30, 12)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("My brilliant idea about caching", "my-brilliant-idea-about-caching"),
        ("  Hello,   World!  ", "hello-world"),
        ("C++ & Rust: 2 langs", "c-rust-2-langs"),
        ("!!!", ""),
        ("", ""),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected


def test_slugify_caps_length_without_trailing_dash():
    slug = slugify("a" * 49 + " bbbb")
    assert len(slug) <= 50
    assert not slug.endswith("-")
    assert slug == "a" * 49


def test_note_filename_uses_timestamp_and_slug():
    name = note_filename("My brilliant idea about caching", NOW)
    assert name == "2026-10-28-143012-my-brilliant-idea-about-caching.md"


def test_note_filename_falls_back_to_timestamp_only():
    assert note_filename("!!!", NOW) == "2026-10-28-143012.md"


def test_render_note_has_heading_and_full_text():
    text = "First line\nsecond line"
    assert render_note(text) == "# First line\n\nFirst line\nsecond line\n"


def test_render_note_strips_surrounding_whitespace():
    assert render_note("  idea  \n") == "# idea\n\nidea\n"


def test_save_note_writes_file(tmp_path):
    path = save_note("My idea", tmp_path, NOW)
    assert path == tmp_path / "2026-10-28-143012-my-idea.md"
    assert path.read_text(encoding="utf-8") == "# My idea\n\nMy idea\n"


def test_save_note_creates_missing_directory(tmp_path):
    target = tmp_path / "nested" / "notes"
    path = save_note("idea", target, NOW)
    assert path.parent == target
    assert path.exists()


def test_save_note_never_overwrites(tmp_path):
    first = save_note("same", tmp_path, NOW)
    second = save_note("same", tmp_path, NOW)
    third = save_note("same", tmp_path, NOW)
    assert first.name == "2026-10-28-143012-same.md"
    assert second.name == "2026-10-28-143012-same-2.md"
    assert third.name == "2026-10-28-143012-same-3.md"
    assert first.read_text(encoding="utf-8") == "# same\n\nsame\n"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_save_note_rejects_empty_text(tmp_path, text):
    with pytest.raises(ValueError):
        save_note(text, tmp_path, NOW)
    assert list(tmp_path.iterdir()) == []


def test_notes_dir_defaults_to_home(monkeypatch, tmp_path):
    monkeypatch.delenv("SECOND_BRAIN_DIR")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert notes_dir() == tmp_path / DEFAULT_DIR_NAME
    assert DEFAULT_DIR_NAME == "second_brain"


def test_notes_dir_reads_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path / "brain"))
    assert notes_dir() == tmp_path / "brain"


def test_notes_dir_expands_tilde(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("SECOND_BRAIN_DIR", "~/brain")
    assert notes_dir() == Path(tmp_path) / "brain"
