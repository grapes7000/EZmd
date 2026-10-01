"""Build 02 formatting is in memory; existing safe Save writes only plain text."""

from pathlib import Path

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow


def test_formatted_document_saves_its_plain_utf8_text(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "draft notes 文書.md"
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setPlainText("Café\n第二行")
    cursor = window.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.bold_action.trigger()
    window.style_selector.setCurrentIndex(1)
    window.bullet_action.trigger()
    window.quote_action.trigger()

    def selected(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    assert path.read_bytes() == "Café\n第二行".encode()
    assert window.current_path == path
    assert not window.editor.document().isModified()
