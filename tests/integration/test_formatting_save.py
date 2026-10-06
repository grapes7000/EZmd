"""Saving and reopening preserves the formatting EZmd exposes in its toolbar."""

from pathlib import Path

import pytest
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextFormat, QTextListFormat
from PySide6.QtWidgets import QFileDialog
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow


def test_quote_after_lists_reopens_as_quote_text(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setPlainText("Bullet\nNumber\nQuote")
    for index, action in (
        (0, window.bullet_action),
        (1, window.numbered_action),
        (2, window.quote_action),
    ):
        window.editor.setTextCursor(QTextCursor(window.editor.document().findBlockByNumber(index)))
        action.trigger()

    path = tmp_path / "quote.md"

    def selected(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    assert path.read_text(encoding="utf-8") == "- Bullet\n1.  Number\n\n> Quote\n\n"

    window.new_document()
    monkeypatch.setattr(QFileDialog, "getOpenFileName", selected)
    window.open_document()
    document = window.editor.document()
    assert document.findBlockByNumber(0).textList().format().style() == (
        QTextListFormat.Style.ListDisc
    )
    assert document.findBlockByNumber(1).textList().format().style() == (
        QTextListFormat.Style.ListDecimal
    )
    quote = document.findBlockByNumber(2)
    assert quote.text() == "Quote"
    assert quote.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1
    assert not quote.begin().fragment().charFormat().fontFamilies()


def test_toolbar_formatting_survives_save_and_reopen(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "draft notes 文書.md"
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setPlainText(
        "Paragraph\nHeading one\nHeading two\nHeading three\nbold italic struck\nBullet\nNumber\nQuote"
    )

    def select_block(index: int) -> None:
        cursor = QTextCursor(window.editor.document().findBlockByNumber(index))
        window.editor.setTextCursor(cursor)

    for index, level in ((1, 1), (2, 2), (3, 3)):
        select_block(index)
        window.style_selector.setCurrentIndex(level)

    for text, action in (
        ("bold", window.bold_action),
        ("italic", window.italic_action),
        ("struck", window.strike_action),
    ):
        cursor = window.editor.textCursor()
        start = window.editor.toPlainText().index(text)
        cursor.setPosition(start)
        cursor.setPosition(start + len(text), QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        action.trigger()

    for index, action in (
        (5, window.bullet_action),
        (6, window.numbered_action),
        (7, window.quote_action),
    ):
        select_block(index)
        action.trigger()

    document = window.editor.document()
    original_text = window.editor.toPlainText()
    cursor = window.editor.textCursor()
    cursor.setPosition(2)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    selection = (cursor.anchor(), cursor.position())
    undo_steps = document.availableUndoSteps()

    def selected(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    saved = path.read_text(encoding="utf-8")
    assert "# Heading one" in saved
    assert "**bold**" in saved
    assert "*italic*" in saved
    assert "~~struck~~" in saved
    assert "> Quote" in saved
    assert "- Bullet" in saved
    assert (window.editor.textCursor().anchor(), window.editor.textCursor().position()) == selection
    assert document.availableUndoSteps() == undo_steps
    assert not document.isModified()

    window.new_document()
    monkeypatch.setattr(QFileDialog, "getOpenFileName", selected)
    window.open_document()
    reopened = window.editor.document()
    assert window.editor.toPlainText() == original_text
    assert [reopened.findBlockByNumber(i).blockFormat().headingLevel() for i in range(4)] == [
        0,
        1,
        2,
        3,
    ]
    inline = reopened.findBlockByNumber(4)
    fragments: dict[str, QTextCharFormat] = {}
    iterator = inline.begin()
    while not iterator.atEnd():
        fragment = iterator.fragment()
        fragments[fragment.text()] = fragment.charFormat()
        iterator += 1
    assert fragments["bold"].fontWeight() >= QFont.Weight.Bold
    assert fragments["italic"].fontItalic()
    assert fragments["struck"].fontStrikeOut()
    assert reopened.findBlockByNumber(5).textList().format().style() == (
        QTextListFormat.Style.ListDisc
    )
    assert reopened.findBlockByNumber(6).textList().format().style() == (
        QTextListFormat.Style.ListDecimal
    )
    assert (
        reopened.findBlockByNumber(7).blockFormat().property(QTextFormat.Property.BlockQuoteLevel)
        == 1
    )
    assert not reopened.isModified()
    assert not reopened.isUndoAvailable()
