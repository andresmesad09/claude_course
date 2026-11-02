from datetime import datetime
from pathlib import Path

import pytest

from second_brain.notes import (
    DEFAULT_DIR_NAME,
    list_notes,
    note_by_number,
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


def test_list_notes_newest_first(tmp_path):
    for name in [
        "2026-10-28-143012-b.md",
        "2026-10-31-091500-c.md",
        "2026-01-01-000000-a.md",
    ]:
        (tmp_path / name).write_text("x")
    assert [p.name for p in list_notes(tmp_path)] == [
        "2026-10-31-091500-c.md",
        "2026-10-28-143012-b.md",
        "2026-01-01-000000-a.md",
    ]


def test_list_notes_only_top_level_visible_markdown_files(tmp_path):
    (tmp_path / "2026-10-28-143012-note.md").write_text("x")
    (tmp_path / "notes.txt").write_text("x")
    (tmp_path / ".DS_Store").write_text("x")
    (tmp_path / ".hidden.md").write_text("x")
    (tmp_path / "._2026-10-28-143012-note.md").write_text("x")
    (tmp_path / "folder.md").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "2026-10-29-000000-nested.md").write_text("x")
    assert [p.name for p in list_notes(tmp_path)] == ["2026-10-28-143012-note.md"]


def test_list_notes_missing_folder_is_empty_and_not_created(tmp_path):
    missing = tmp_path / "missing"
    assert list_notes(missing) == []
    assert not missing.exists()


def test_list_notes_empty_folder(tmp_path):
    assert list_notes(tmp_path) == []


def test_list_notes_same_second_duplicate_sorts_below_original(tmp_path):
    # Known, accepted quirk (see #5): "-" sorts before ".", so the newer
    # "-2" duplicate of a same-second note is listed below the original.
    first = save_note("same", tmp_path, NOW)
    second = save_note("same", tmp_path, NOW)
    assert list_notes(tmp_path) == [first, second]


def _three_notes(directory):
    names = [
        "2026-01-01-000000-a.md",
        "2026-10-28-143012-b.md",
        "2026-10-31-091500-c.md",
    ]
    for name in names:
        (directory / name).write_text("x")


def test_note_by_number_matches_list_order(tmp_path):
    _three_notes(tmp_path)
    assert note_by_number(tmp_path, 1).name == "2026-10-31-091500-c.md"
    assert note_by_number(tmp_path, 3).name == "2026-01-01-000000-a.md"


def test_note_by_number_out_of_range(tmp_path):
    _three_notes(tmp_path)
    assert note_by_number(tmp_path, 4) is None


def test_note_by_number_empty_and_missing_folder(tmp_path):
    assert note_by_number(tmp_path, 1) is None
    missing = tmp_path / "missing"
    assert note_by_number(missing, 1) is None
    assert not missing.exists()
