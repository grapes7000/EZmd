"""Real, disposable document files and safe replacement behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QByteArray, QSaveFile

from ezmd.core import files


def test_read_text_uses_utf8_and_normalizes_windows_newlines(tmp_path: Path) -> None:
    path = tmp_path / "my notes é" / "文書.markdown"
    path.parent.mkdir()
    path.write_bytes("Café\r\n第二行\r\n".encode())

    assert files.read_text(path) == "Café\n第二行\n"


def test_invalid_utf8_is_reported_instead_of_silently_replaced(tmp_path: Path) -> None:
    path = tmp_path / "invalid.md"
    path.write_bytes(b"Some text\xff")

    with pytest.raises(UnicodeDecodeError):
        files.read_text(path)


def test_save_writes_utf8_lf_and_replaces_existing_contents(tmp_path: Path) -> None:
    path = tmp_path / "my notes é.md"
    files.write_text(path, "Café\r\n第二行\r\n")
    assert path.read_bytes() == "Café\n第二行\n".encode()

    files.write_text(path, "Final 📝\n")
    assert path.read_bytes() == "Final 📝\n".encode()


def test_partial_write_cannot_truncate_the_previous_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "existing.md"
    path.write_text("Previous work", encoding="utf-8")

    class PartialWrite(QSaveFile):
        def write(self, data: QByteArray | bytes | bytearray | memoryview[int]) -> int:
            if isinstance(data, QByteArray):
                data = data.data()
            super().write(bytes(data[:1]))
            return 1

    monkeypatch.setattr(files, "QSaveFile", PartialWrite)

    with pytest.raises(OSError):
        files.write_text(path, "Replacement text")
    assert path.read_text(encoding="utf-8") == "Previous work"


def test_unavailable_destination_reports_failure_without_changing_text_file(tmp_path: Path) -> None:
    path = tmp_path / "existing.md"
    path.write_text("Previous work", encoding="utf-8")

    with pytest.raises(OSError):
        files.write_text(tmp_path / "missing directory" / "new.md", "Replacement")
    assert path.read_text(encoding="utf-8") == "Previous work"
