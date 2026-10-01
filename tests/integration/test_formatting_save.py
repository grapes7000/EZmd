"""Supported visual formatting is durable canonical Markdown."""

from pathlib import Path

import pytest
from PySide6.QtGui import QTextCursor, QTextFormat, QTextListFormat
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow


def test_formatted_document_saves_and_reopens_with_semantics(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "draft notes 文書.md"
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setPlainText("Café\nSecond")
    cursor = window.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.bold_action.trigger()
    window.style_selector.setCurrentIndex(2)
    window.quote_action.trigger()
    cursor.setPosition(5)
    window.editor.setTextCursor(cursor)
    window.numbered_action.trigger()

    def save_path(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", save_path)
    assert window.save_document()
    assert path.read_bytes() == "> ## **Café**\n\n1. Second\n".encode()

    window.new_document()

    def open_path(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", open_path)
    window.open_document()
    document = window.editor.document()
    first = document.begin()
    second = first.next()
    assert window.editor.toPlainText() == "Café\nSecond"
    assert first.blockFormat().headingLevel() == 2
    assert first.blockFormat().intProperty(QTextFormat.Property.BlockQuoteLevel) == 1
    assert first.begin().fragment().charFormat().fontWeight() > 400
    assert second.textList().format().style() == QTextListFormat.Style.ListDecimal
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    window.editor.setTextCursor(cursor)
    assert window.style_selector.currentIndex() == 2
    assert window.bold_action.isChecked()
    assert window.quote_action.isChecked()
    assert not document.isModified()
    assert not document.isUndoAvailable()
    window.editor.insertPlainText("!")
    assert document.isUndoAvailable()
    window.editor.undo()
    assert window.editor.toPlainText() == "Café\nSecond"
