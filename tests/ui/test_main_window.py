"""Real Qt interaction with one editable document and its file actions."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QByteArray, QMimeData, QSaveFile, Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QToolButton
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow
from ezmd.ui.visual_profiles import DEFAULT_PROFILE, PROFILES


@pytest.fixture
def window(qtbot: QtBot) -> Iterator[MainWindow]:
    def make_clean(widget: MainWindow) -> None:
        widget.editor.document().setModified(False)

    window = MainWindow()
    qtbot.addWidget(window, before_close_func=make_clean)
    window.show()
    yield window


def type_text(window: MainWindow, text: str) -> None:
    QTest.keyClicks(window.editor, text)


def save_to(monkeypatch: pytest.MonkeyPatch, filename: str) -> None:
    def selected(*_args: object) -> tuple[str, str]:
        return filename, ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)


def open_from(monkeypatch: pytest.MonkeyPatch, filename: str) -> None:
    def selected(*_args: object) -> tuple[str, str]:
        return filename, ""

    monkeypatch.setattr(QFileDialog, "getOpenFileName", selected)


def record_error(monkeypatch: pytest.MonkeyPatch, errors: list[str]) -> None:
    def capture(_parent: object, _title: str, text: str) -> None:
        errors.append(text)

    monkeypatch.setattr(QMessageBox, "critical", capture)


def choose_prompt(button: QMessageBox.StandardButton) -> None:
    def click() -> None:
        dialog = QApplication.activeModalWidget()
        assert isinstance(dialog, QMessageBox)
        choice = dialog.button(button)
        assert choice is not None
        choice.click()

    QTimer.singleShot(0, click)


def test_window_has_a_usable_editor_and_typing_marks_it_modified(
    qtbot: QtBot, window: MainWindow
) -> None:
    assert window.findChildren(type(window.editor)) == [window.editor]
    assert window.editor.toPlainText() == ""
    assert window.current_path is None
    assert not window.editor.document().isModified()
    assert window.profile_actions[DEFAULT_PROFILE].isChecked()

    type_text(window, "Draft")
    assert window.editor.toPlainText() == "Draft"
    assert window.editor.document().isModified()
    assert "Untitled *" in window.windowTitle()


def test_menus_and_toolbar_place_actions_and_share_native_undo_history(
    qtbot: QtBot, window: MainWindow
) -> None:
    menu_actions = [
        action for menu in window.menuBar().findChildren(QMenu) for action in menu.actions()
    ]
    for action, standard in (
        (window.new_action, QKeySequence.StandardKey.New),
        (window.open_action, QKeySequence.StandardKey.Open),
        (window.save_action, QKeySequence.StandardKey.Save),
        (window.undo_action, QKeySequence.StandardKey.Undo),
        (window.redo_action, QKeySequence.StandardKey.Redo),
    ):
        assert action in menu_actions
        assert action.shortcut() == QKeySequence(standard)
    for action in (window.new_action, window.open_action, window.save_action):
        assert window.toolbar.widgetForAction(action) is None
    for action in (window.undo_action, window.redo_action):
        assert window.toolbar.widgetForAction(action) is not None
    for name, action in window.profile_actions.items():
        assert action.text() == name
        assert action in menu_actions
        assert window.toolbar.widgetForAction(action) is None
    menus = {menu.title().replace("&", ""): menu for menu in window.menuBar().findChildren(QMenu)}
    for name, expected in (
        ("File", (window.new_action, window.open_action, window.save_action)),
        ("Edit", (window.undo_action, window.redo_action)),
    ):
        assert all(action in menus[name].actions() for action in expected)
    assert "Visual Profile" in [action.text() for action in menus["View"].actions()]

    type_text(window, "Hello")
    window.undo_action.trigger()
    assert window.editor.toPlainText() != "Hello"
    window.redo_action.trigger()
    assert window.editor.toPlainText() == "Hello"


def test_new_on_clean_document_clears_text_path_and_modified_state(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Existing")
    path = tmp_path / "existing.md"
    save_to(monkeypatch, str(path))
    assert window.save_document()

    window.new_action.trigger()
    assert window.editor.toPlainText() == ""
    assert window.current_path is None
    assert not window.editor.document().isModified()
    assert "Untitled" in window.windowTitle()


def test_new_document_resets_insertion_point_formatting(window: MainWindow) -> None:
    window.bold_action.trigger()
    window.italic_action.trigger()
    window.strike_action.trigger()
    window.new_document()

    type_text(window, "Plain")
    char_format = window.editor.document().begin().begin().fragment().charFormat()
    assert char_format.fontWeight() == QFont.Weight.Normal
    assert not char_format.fontItalic()
    assert not char_format.fontStrikeOut()


def test_canceling_new_keeps_unsaved_text_cursor_selection_and_path(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "original.md"
    path.write_text("Original", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_action.trigger()
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, "Draft")
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)

    choose_prompt(QMessageBox.StandardButton.Cancel)
    window.new_action.trigger()
    assert window.editor.toPlainText() == "OriginalDraft"
    assert (window.editor.textCursor().anchor(), window.editor.textCursor().position()) == (1, 4)
    assert window.current_path == path
    assert window.editor.document().isModified()


def test_canceling_open_does_not_show_the_picker_or_discard_text(
    qtbot: QtBot, window: MainWindow, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Draft")

    def unexpected_picker(*args: object) -> tuple[str, str]:
        pytest.fail("Open picker must not run after Cancel")

    monkeypatch.setattr(QFileDialog, "getOpenFileName", unexpected_picker)
    choose_prompt(QMessageBox.StandardButton.Cancel)
    window.open_action.trigger()
    assert window.editor.toPlainText() == "Draft"
    assert window.editor.document().isModified()


def test_canceling_close_keeps_the_window_and_document_alive(
    qtbot: QtBot, window: MainWindow
) -> None:
    type_text(window, "Important")
    choose_prompt(QMessageBox.StandardButton.Cancel)
    assert not window.close()
    assert window.isVisible()
    assert window.editor.toPlainText() == "Important"
    assert window.editor.document().isModified()


def test_save_writes_before_close(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Important")
    path = tmp_path / "important.md"
    save_to(monkeypatch, str(path))
    choose_prompt(QMessageBox.StandardButton.Save)
    assert window.close()
    assert path.read_text(encoding="utf-8") == "Important\n"


def test_discard_allows_close(qtbot: QtBot, window: MainWindow) -> None:
    type_text(window, "Discard me")
    choose_prompt(QMessageBox.StandardButton.Discard)
    assert window.close()
    assert not window.isVisible()


def test_discard_and_save_choices_only_proceed_when_allowed(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Keep")
    choose_prompt(QMessageBox.StandardButton.Save)
    save_to(monkeypatch, "")
    window.new_action.trigger()
    assert window.editor.toPlainText() == "Keep"
    assert window.editor.document().isModified()

    path = tmp_path / "saved.md"
    save_to(monkeypatch, str(path))
    choose_prompt(QMessageBox.StandardButton.Save)
    window.new_action.trigger()
    assert path.read_text(encoding="utf-8") == "Keep\n"
    assert window.editor.toPlainText() == ""
    assert window.current_path is None

    type_text(window, "Discard")
    choose_prompt(QMessageBox.StandardButton.Discard)
    window.new_action.trigger()
    assert window.editor.toPlainText() == ""
    assert not window.editor.document().isModified()


def test_first_save_and_later_save_use_same_unicode_path(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "my notes 文書.md"
    type_text(window, "Caf")
    window.editor.insertPlainText("é")
    save_to(monkeypatch, str(path))
    window.save_action.trigger()
    assert path.read_bytes() == "Café\n".encode()
    assert window.current_path == path
    assert not window.editor.document().isModified()
    assert path.name in window.windowTitle()

    type_text(window, " encore")

    def unexpected_picker(*_args: object) -> tuple[str, str]:
        pytest.fail("second save opened picker")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", unexpected_picker)
    window.save_action.trigger()
    assert path.read_text(encoding="utf-8") == "Café encore\n"
    assert not window.editor.document().isModified()


def test_cancel_save_destination_leaves_document_and_disk_unchanged(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Draft")
    save_to(monkeypatch, "")
    window.save_action.trigger()
    assert window.current_path is None
    assert window.editor.toPlainText() == "Draft"
    assert window.editor.document().isModified()
    assert list(tmp_path.iterdir()) == []


def test_open_utf8_markdown_loads_visual_heading_path_and_clean_state(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "note 文書.markdown"
    path.write_text("# Café\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_action.trigger()
    assert window.editor.toPlainText() == "Café"
    assert window.editor.document().begin().blockFormat().headingLevel() == 1
    assert window.current_path == path
    assert not window.editor.document().isModified()
    assert path.name in window.windowTitle()


def test_open_after_saving_unsaved_work_keeps_the_old_file(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_path = tmp_path / "old.md"
    next_path = tmp_path / "next.txt"
    next_path.write_text("Next document", encoding="utf-8")
    type_text(window, "Old draft")
    save_to(monkeypatch, str(old_path))
    open_from(monkeypatch, str(next_path))

    choose_prompt(QMessageBox.StandardButton.Save)
    window.open_action.trigger()
    assert old_path.read_text(encoding="utf-8") == "Old draft\n"
    assert window.editor.toPlainText() == "Next document"
    assert window.current_path is None
    assert window.suggested_save_path == next_path.with_suffix(".md")
    assert window.editor.document().isModified()


def test_txt_import_is_literal_and_first_save_defaults_to_markdown(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "import me 文書.txt"
    source.write_text("# literal\n**stars**", encoding="utf-8")
    open_from(monkeypatch, str(source))
    window.open_action.trigger()
    assert window.editor.toPlainText() == "# literal\n**stars**"
    assert window.editor.document().begin().blockFormat().headingLevel() == 0
    assert window.current_path is None
    assert window.suggested_save_path == source.with_suffix(".md")
    assert window.editor.document().isModified()

    requested: list[str] = []

    def selected(_parent: object, _title: str, initial: str, _filter: str) -> tuple[str, str]:
        requested.append(initial)
        return str(tmp_path / "imported"), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    destination = tmp_path / "imported.md"
    assert requested == [str(source.with_suffix(".md"))]
    assert destination.read_text(encoding="utf-8") == "\\# literal\n\n\\*\\*stars\\*\\*\n"
    assert source.read_text(encoding="utf-8") == "# literal\n**stars**"
    assert window.current_path == destination


def test_empty_txt_import_and_empty_new_markdown_save_are_valid(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "empty.txt"
    source.write_text("", encoding="utf-8")
    open_from(monkeypatch, str(source))
    window.open_document()
    assert window.editor.toPlainText() == ""
    assert window.current_path is None
    assert window.editor.document().isModified()

    destination = tmp_path / "empty note"
    save_to(monkeypatch, str(destination))
    assert window.save_document()
    markdown_path = destination.with_suffix(".md")
    assert markdown_path.read_bytes() == b""
    assert window.current_path == markdown_path
    assert source.read_bytes() == b""


def test_conflicting_save_extension_is_refused(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Draft")
    destination = tmp_path / "draft.txt"
    save_to(monkeypatch, str(destination))
    errors: list[str] = []
    record_error(monkeypatch, errors)
    assert not window.save_document()
    assert errors and ".md or .markdown" in errors[0]
    assert window.current_path is None
    assert window.editor.document().isModified()
    assert not destination.exists()


def test_unsupported_markdown_open_preserves_all_current_state(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    current = tmp_path / "current.md"
    current.write_text("Current", encoding="utf-8")
    open_from(monkeypatch, str(current))
    window.open_action.trigger()
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, " edit")
    cursor = window.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(7, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.bold_action.trigger()
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    document = window.editor.document()
    before = (
        window.editor.toPlainText(),
        window.current_path,
        document.isModified(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        cursor.anchor(),
        cursor.position(),
        document.begin().begin().fragment().charFormat().fontWeight(),
    )
    unsupported = tmp_path / "unsupported.md"
    unsupported.write_text("[link](target)\n", encoding="utf-8")
    open_from(monkeypatch, str(unsupported))
    errors: list[str] = []
    record_error(monkeypatch, errors)
    choose_prompt(QMessageBox.StandardButton.Discard)
    window.open_action.trigger()
    current_cursor = window.editor.textCursor()
    assert errors and "Links and images" in errors[0]
    assert (
        window.editor.toPlainText(),
        window.current_path,
        document.isModified(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        current_cursor.anchor(),
        current_cursor.position(),
        document.begin().begin().fragment().charFormat().fontWeight(),
    ) == before
    assert unsupported.read_text(encoding="utf-8") == "[link](target)\n"


def test_save_preserves_selection_formatting_and_undo_history(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window.editor.setPlainText("Formatted text")
    cursor = window.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(9, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    window.bold_action.trigger()
    cursor.setPosition(8)
    cursor.setPosition(2, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    document = window.editor.document()
    before = (
        cursor.anchor(),
        cursor.position(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        document.begin().begin().fragment().charFormat().fontWeight(),
    )
    path = tmp_path / "selection.md"
    save_to(monkeypatch, str(path))
    assert window.save_document()
    cursor = window.editor.textCursor()
    assert (
        cursor.anchor(),
        cursor.position(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        document.begin().begin().fragment().charFormat().fontWeight(),
    ) == before
    assert not document.isModified()


def test_serialization_failure_keeps_dirty_document_and_path(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "existing.md"
    path.write_text("Previous\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    type_text(window, " edit")
    document = window.editor.document()
    before = (window.editor.toPlainText(), document.availableUndoSteps())

    def failed_serialization(_document: object) -> str:
        from ezmd.core.markdown import MarkdownError

        raise MarkdownError("unsupported document state")

    monkeypatch.setattr("ezmd.ui.main_window.serialize_markdown", failed_serialization)
    errors: list[str] = []
    record_error(monkeypatch, errors)
    assert not window.save_document()
    assert errors and "unsupported document state" in errors[0]
    assert (window.editor.toPlainText(), document.availableUndoSteps()) == before
    assert window.current_path == path
    assert document.isModified()
    assert path.read_text(encoding="utf-8") == "Previous\n"


def test_normal_editing_and_profile_switching_do_not_run_markdown_conversion(
    window: MainWindow, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected(*_args: object) -> object:
        pytest.fail("Markdown conversion ran outside Open or Save")

    monkeypatch.setattr("ezmd.ui.main_window.parse_markdown", unexpected)
    monkeypatch.setattr("ezmd.ui.main_window.serialize_markdown", unexpected)
    type_text(window, "ordinary typing")
    window.editor.moveCursor(QTextCursor.MoveOperation.Start)
    window.editor.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
    window.bold_action.trigger()
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()


def test_open_after_discard_replaces_unsaved_work_without_saving_it(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    next_path = tmp_path / "next.md"
    next_path.write_text("Next document", encoding="utf-8")
    type_text(window, "Unsaved")
    open_from(monkeypatch, str(next_path))

    choose_prompt(QMessageBox.StandardButton.Discard)
    window.open_action.trigger()
    assert window.editor.toPlainText() == "Next document"
    assert window.current_path == next_path
    assert not window.editor.document().isModified()
    assert list(tmp_path.iterdir()) == [next_path]


def test_failed_open_after_discard_keeps_old_text_path_and_modified_state(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_path = tmp_path / "old.md"
    old_path.write_text("Old", encoding="utf-8")
    open_from(monkeypatch, str(old_path))
    window.open_action.trigger()
    type_text(window, " edit")
    before = window.editor.toPlainText()
    missing_path = tmp_path / "missing.md"
    open_from(monkeypatch, str(missing_path))
    errors: list[str] = []
    record_error(monkeypatch, errors)

    choose_prompt(QMessageBox.StandardButton.Discard)
    window.open_action.trigger()
    assert errors and "missing.md" in errors[0]
    assert window.editor.toPlainText() == before
    assert window.current_path == old_path
    assert window.editor.document().isModified()


def test_failed_save_preserves_document_path_and_old_disk_file(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "old.md"
    path.write_text("Old", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_action.trigger()
    type_text(window, " edit")
    before = window.editor.toPlainText()

    def failed_write(path: Path, text: str) -> None:
        raise OSError("disk unavailable")

    monkeypatch.setattr("ezmd.ui.main_window.write_text", failed_write)
    errors: list[str] = []
    record_error(monkeypatch, errors)
    window.save_action.trigger()
    assert errors and "disk unavailable" in errors[0]
    assert window.editor.toPlainText() == before
    assert window.current_path == path
    assert window.editor.document().isModified()
    assert path.read_text(encoding="utf-8") == "Old"


def test_failed_first_save_keeps_untitled_draft_unassociated(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Important draft")
    path = tmp_path / "new note 文書.md"
    save_to(monkeypatch, str(path))

    class PartialWrite(QSaveFile):
        def write(self, data: QByteArray | bytes | bytearray | memoryview[int]) -> int:
            if isinstance(data, QByteArray):
                data = data.data()
            super().write(bytes(data[:1]))
            return 1

    monkeypatch.setattr("ezmd.core.files.QSaveFile", PartialWrite)
    errors: list[str] = []
    record_error(monkeypatch, errors)

    window.save_action.trigger()
    assert errors and f"Could not save {path.name}" in errors[0]
    assert window.editor.toPlainText() == "Important draft"
    assert window.current_path is None
    assert window.editor.document().isModified()
    assert "Untitled *" in window.windowTitle()
    assert not path.exists()


def test_failed_save_in_unsaved_prompt_prevents_new_and_close(
    qtbot: QtBot, window: MainWindow, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Important")
    save_to(monkeypatch, "")
    choose_prompt(QMessageBox.StandardButton.Save)
    window.new_action.trigger()
    assert window.editor.toPlainText() == "Important"

    choose_prompt(QMessageBox.StandardButton.Save)
    assert not window.close()
    assert window.isVisible()
    assert window.editor.document().isModified()


def test_rich_user_insertion_stays_plain_text_in_the_editor(window: MainWindow) -> None:
    pasted = QMimeData()
    pasted.setHtml("<strong>Bold</strong>")
    pasted.setText("Bold")

    window.editor.insertFromMimeData(pasted)
    assert window.editor.toPlainText() == "Bold"
    assert window.editor.textCursor().charFormat().fontWeight() == QFont.Weight.Normal
    assert window.editor.document().isModified()


def test_live_profiles_keep_document_cursor_selection_undo_and_path(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "work.md"
    type_text(window, "Some writing")
    save_to(monkeypatch, str(path))
    assert window.save_document()
    type_text(window, " more")
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    before = window.editor.toPlainText()
    before_cursor = (cursor.anchor(), cursor.position())
    document = window.editor.document()
    undo_steps = document.availableUndoSteps()
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        assert window.profile_actions[name].isChecked()
        margin = PROFILES[name].content_margin
        assert window.content_layout.contentsMargins().left() == margin
        assert window.content_layout.contentsMargins().right() == margin
        assert window.editor.toPlainText() == before
        assert (window.editor.textCursor().anchor(), window.editor.textCursor().position()) == (
            before_cursor
        )
        assert window.current_path == path
        assert document.isModified()
        assert document.availableUndoSteps() == undo_steps
        assert not document.isRedoAvailable()
    window.editor.undo()
    assert window.editor.toPlainText() != before
    after_undo = window.editor.toPlainText()
    undo_steps = document.availableUndoSteps()
    assert document.isRedoAvailable()
    modified = document.isModified()
    for name in ("QTemp", "Lab", "Focus"):
        window.profile_actions[name].trigger()
        assert window.editor.toPlainText() == after_undo
        assert document.isModified() == modified
        assert document.availableUndoSteps() == undo_steps
        assert document.isRedoAvailable()
    window.editor.redo()
    assert window.editor.toPlainText() == before


def test_focus_buttons_are_quiet_at_rest_while_other_profiles_retain_boundaries(
    window: MainWindow,
) -> None:
    assert PROFILES["Focus"].quiet_buttons_at_rest
    assert not PROFILES["Lab"].quiet_buttons_at_rest
    assert not PROFILES["QTemp"].quiet_buttons_at_rest

    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        assert window.profile_actions[name].isChecked()
        assert not window.editor.document().isModified()
        assert window.editor.document().availableUndoSteps() == 0
        for action in (
            window.undo_action,
            window.redo_action,
            window.bold_action,
            window.italic_action,
            window.strike_action,
            window.bullet_action,
            window.numbered_action,
            window.quote_action,
        ):
            button = window.toolbar.widgetForAction(action)
            assert isinstance(button, QToolButton)
            assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus
