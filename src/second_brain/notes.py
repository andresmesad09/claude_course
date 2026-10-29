"""Save quick thoughts as plain markdown notes."""

import os
import re
from pathlib import Path

DEFAULT_DIR_NAME = "second_brain"
MAX_SLUG_LENGTH = 50


def notes_dir():
    """Return the folder notes are saved in.

    Reads SECOND_BRAIN_DIR (``~`` is expanded) and falls back to
    ``~/second_brain``.
    """
    configured = os.environ.get("SECOND_BRAIN_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / DEFAULT_DIR_NAME


def slugify(text):
    """Turn text into a lowercase, dash-separated slug of at most 50 chars."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:MAX_SLUG_LENGTH].rstrip("-")


def note_filename(text, now):
    """Return ``YYYY-MM-DD-HHMMSS-<slug>.md``, or just the timestamp if no slug."""
    stem = now.strftime("%Y-%m-%d-%H%M%S")
    slug = slugify(text)
    if slug:
        stem = f"{stem}-{slug}"
    return f"{stem}.md"


def render_note(text):
    """Render a note as an H1 of the first line, a blank line, then the text."""
    text = text.strip()
    heading = text.splitlines()[0]
    return f"# {heading}\n\n{text}\n"


def save_note(text, directory, now):
    """Write text as a new note in directory and return its path.

    Never overwrites: a taken name gets a ``-2``, ``-3``, ... suffix.
    Raises ValueError if text is empty or whitespace-only.
    """
    if not text.strip():
        raise ValueError("A note can't be empty.")
    directory.mkdir(parents=True, exist_ok=True)
    content = render_note(text)
    base = Path(note_filename(text, now))
    path = directory / base
    suffix = 2
    while True:
        try:
            with path.open("x", encoding="utf-8") as f:
                f.write(content)
            return path
        except FileExistsError:
            path = directory / f"{base.stem}-{suffix}{base.suffix}"
            suffix += 1
