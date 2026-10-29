"""Shared test fixtures."""

import pytest


@pytest.fixture(autouse=True)
def _test_log_file(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))


@pytest.fixture(autouse=True)
def _test_notes_dir(tmp_path, monkeypatch):
    """Keep tests away from the real ~/second_brain and the developer's .env."""
    monkeypatch.setenv("SECOND_BRAIN_DIR", str(tmp_path / "notes"))
    monkeypatch.chdir(tmp_path)
