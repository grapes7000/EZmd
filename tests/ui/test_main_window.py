"""Real Qt interaction with one editable document and its file actions."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QByteArray, QMimeData, QPoint, QSaveFile, Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QPalette, QTextCursor, QTextDocument, QTextFormat
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox, QToolButton
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow
from ezmd.ui.visual_profiles import DEFAULT_PROFILE, DEFAULT_THEME, PROFILES, THEMES


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


def test_toolbar_belongs_to_editor_pane_not_main_window_toolbar_area(window: MainWindow) -> None:
    assert window.centralWidget() is window.splitter
    assert window.splitter.widget(0) is window.sidebar
    assert window.splitter.widget(1) is window.editor_pane
    assert window.toolbar.parentWidget() is window.editor_pane
    assert window.editor.parentWidget() is window.editor_pane
    assert window.toolBarArea(window.toolbar) == Qt.ToolBarArea.NoToolBarArea


def test_editor_pane_places_toolbar_above_editor(window: MainWindow) -> None:
    pane_layout = window.editor_pane.layout()
    assert pane_layout is not None
    toolbar_item = pane_layout.itemAt(0)
    content_item = pane_layout.itemAt(1)
    editor_item = window.content_layout.itemAt(0)
    assert toolbar_item is not None and toolbar_item.widget() is window.toolbar
    assert content_item is not None and content_item.layout() is window.content_layout
    assert editor_item is not None and editor_item.widget() is window.editor
    assert window.toolbar.isVisible()
    assert window.editor.isVisible()
    assert window.toolbar.geometry().bottom() < window.editor.geometry().top()


def test_sidebar_resizes_without_extending_toolbar_over_it(window: MainWindow) -> None:
    window.resize(1000, 680)
    window.splitter.setSizes([240, 760])
    before = window.sidebar.width()
    handle = window.splitter.handle(1)
    assert handle is not None
    start = QPoint(handle.width() // 2, handle.height() // 2)
    QTest.mousePress(handle, Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(handle, pos=start + QPoint(40, 0))
    QTest.mouseRelease(handle, Qt.MouseButton.LeftButton, pos=start + QPoint(40, 0))
    assert window.sidebar.width() > before
    assert window.editor_pane.geometry().left() > window.sidebar.geometry().right()
    assert window.toolbar.width() == window.editor_pane.width()


def test_sidebar_collapse_expand_and_hide_restore_previous_mode(window: MainWindow) -> None:
    window.resize(1600, 680)
    window.splitter.setSizes([280, 1320])
    expanded_width = window.sidebar.width()
    editor_left = window.editor_pane.geometry().left()
    editor_width = window.editor_pane.width()
    assert window.show_sidebar_action.isChecked()
    QTest.mouseClick(window.sidebar_collapse_button, Qt.MouseButton.LeftButton)
    assert window.sidebar.width() == 40
    assert window.splitter.sizes()[0] == 40
    assert window.editor_pane.geometry().left() == 40 + window.splitter.handleWidth()
    assert window.editor_pane.width() > editor_width
    assert not window.sidebar_header.isVisible()
    assert window.sidebar_expand_button.isVisible()
    assert window.editor.hasFocus()

    window.show_sidebar_action.trigger()
    assert not window.show_sidebar_action.isChecked()
    assert not window.sidebar.isVisible()
    assert window.editor_pane.width() > window.sidebar.width()
    window.show_sidebar_action.trigger()
    assert window.sidebar.isVisible()
    assert window.sidebar_expand_button.isVisible()
    assert window.sidebar.width() == 40
    assert window.editor_pane.geometry().left() == 40 + window.splitter.handleWidth()

    QTest.mouseClick(window.sidebar_expand_button, Qt.MouseButton.LeftButton)
    assert window.sidebar_header.isVisible()
    assert not window.sidebar_expand_button.isVisible()
    assert abs(window.sidebar.width() - expanded_width) <= 2
    assert abs(window.editor_pane.geometry().left() - editor_left) <= 2
    assert window.editor.hasFocus()
    window.show_sidebar_action.trigger()
    window.show_sidebar_action.trigger()
    assert window.sidebar_header.isVisible()
    assert abs(window.sidebar.width() - expanded_width) <= 2


def test_sidebar_controls_work_from_keyboard_and_do_not_strand_focus(window: MainWindow) -> None:
    window.sidebar_collapse_button.setFocus()
    QTest.keyClick(window.sidebar_collapse_button, Qt.Key.Key_Space)
    assert window.sidebar_expand_button.isVisible()
    assert window.editor.hasFocus()
    window.sidebar_expand_button.setFocus()
    QTest.keyClick(window.sidebar_expand_button, Qt.Key.Key_Space)
    assert window.sidebar_header.isVisible()
    assert window.editor.hasFocus()
    window.sidebar_collapse_button.setFocus()
    window.show_sidebar_action.trigger()
    assert not window.sidebar.isVisible()
    assert window.editor.hasFocus()


def test_sidebar_changes_preserve_document_and_use_existing_themes(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    type_text(window, "Some writing")
    path = tmp_path / "work.md"
    save_to(monkeypatch, str(path))
    assert window.save_document()
    type_text(window, " more")
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    document = window.editor.document()
    before = (
        window.editor.toPlainText(),
        cursor.anchor(),
        cursor.position(),
        document.isModified(),
        document.availableUndoSteps(),
        window.current_path,
    )
    for profile in PROFILES:
        window.profile_actions[profile].trigger()
        for theme in THEMES:
            window.theme_actions[theme].trigger()
            colors = THEMES[theme]
            assert colors.background_elevated in window.sidebar.styleSheet()
            assert colors.focus_ring in window.sidebar.styleSheet()
            assert colors.border in window.splitter.styleSheet()
        window.sidebar_collapse_button.click()
        window.sidebar_expand_button.click()
        window.show_sidebar_action.trigger()
        window.show_sidebar_action.trigger()
        assert (
            window.editor.toPlainText(),
            window.editor.textCursor().anchor(),
            window.editor.textCursor().position(),
            document.isModified(),
            document.availableUndoSteps(),
            window.current_path,
        ) == before
    window.undo_action.trigger()
    assert window.editor.toPlainText() == "Some writing"
    window.redo_action.trigger()
    assert window.editor.toPlainText() == "Some writing more"


def test_narrow_window_keeps_editor_and_toolbar_usable(window: MainWindow) -> None:
    window.resize(640, 480)
    assert window.width() <= 640
    assert window.editor.isVisible()
    assert window.toolbar.isVisible()
    assert window.editor_pane.width() > 0
    assert window.editor.viewport().width() > 0
    assert window.toolbar.width() == window.editor_pane.width()
    window.sidebar_collapse_button.click()
    assert window.editor_pane.width() > window.sidebar.width()


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
    theme_menu = next(
        action.menu() for action in menus["View"].actions() if action.text() == "Color Theme"
    )
    assert isinstance(theme_menu, QMenu)
    assert theme_menu.actions() == list(window.theme_actions.values())

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
    assert path.read_text(encoding="utf-8") == "Important\n\n"


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
    assert path.read_text(encoding="utf-8") == "Keep\n\n"
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
    assert path.read_text(encoding="utf-8") == "Café\n\n"
    assert window.current_path == path
    assert not window.editor.document().isModified()
    assert path.stem in window.windowTitle()
    assert path.name not in window.windowTitle()

    type_text(window, " encore")

    def unexpected_picker(*_args: object) -> tuple[str, str]:
        pytest.fail("second save opened picker")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", unexpected_picker)
    window.save_action.trigger()
    assert path.read_text(encoding="utf-8") == "Café encore\n\n"
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


def test_open_utf8_markdown_file_loads_visual_document_path_and_clean_state(
    qtbot: QtBot, window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "note 文書.markdown"
    path.write_text("# Café\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_action.trigger()
    assert window.editor.toPlainText() == "Café"
    assert window.editor.document().firstBlock().blockFormat().headingLevel() == 1
    assert window.current_path == path
    assert not window.editor.document().isModified()
    assert path.stem in window.windowTitle()
    assert path.name not in window.windowTitle()


def test_opened_markdown_has_no_load_undo_and_edits_use_native_history(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "heading.md"
    path.write_text("# Heading\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    document = window.editor.document()
    assert window.style_selector.currentText() == "H1"
    assert not document.isModified()
    assert not document.isUndoAvailable()
    assert not window.undo_action.isEnabled()
    assert window.editor.hasFocus()

    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, "!")
    assert window.editor.toPlainText() == "Heading!"
    assert document.isModified()
    assert window.undo_action.isEnabled()
    assert "heading *" in window.windowTitle()
    window.undo_action.trigger()
    assert window.editor.toPlainText() == "Heading"
    window.redo_action.trigger()
    assert window.editor.toPlainText() == "Heading!"


def test_failed_markdown_load_preserves_live_document_and_path(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    old_path = tmp_path / "old.md"
    old_path.write_text("# Original\n", encoding="utf-8")
    open_from(monkeypatch, str(old_path))
    window.open_document()
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, " draft")
    document = window.editor.document()
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    cursor.setPosition(4, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)
    undo_steps = document.availableUndoSteps()

    def failed_load(_document: QTextDocument, _text: str) -> None:
        raise RuntimeError("could not load")

    monkeypatch.setattr(QTextDocument, "setMarkdown", failed_load)
    open_from(monkeypatch, str(tmp_path / "next.md"))
    (tmp_path / "next.md").write_text("# Next\n", encoding="utf-8")
    errors: list[str] = []
    record_error(monkeypatch, errors)
    choose_prompt(QMessageBox.StandardButton.Discard)
    window.open_document()
    assert errors and "could not load" in errors[0]
    assert window.editor.document() is document
    assert window.editor.toPlainText() == "Original draft"
    assert (window.editor.textCursor().anchor(), window.editor.textCursor().position()) == (1, 4)
    assert document.availableUndoSteps() == undo_steps
    assert document.isModified()
    assert window.current_path == old_path


def test_normal_editing_does_not_convert_markdown(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "draft.md"
    path.write_text("# Heading\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()

    def unexpected_conversion(*_args: object) -> None:
        pytest.fail("Markdown conversion ran outside Open or Save")

    monkeypatch.setattr(QTextDocument, "setMarkdown", unexpected_conversion)
    monkeypatch.setattr(QTextDocument, "toMarkdown", unexpected_conversion)
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, "!")
    window.style_selector.setCurrentIndex(2)
    window.profile_actions["Lab"].trigger()
    window.editor.moveCursor(QTextCursor.MoveOperation.Start)
    window.undo_action.trigger()
    window.redo_action.trigger()


def test_text_file_stays_literal_after_markdown_open(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    markdown = tmp_path / "first.md"
    markdown.write_text("# Heading\n", encoding="utf-8")
    open_from(monkeypatch, str(markdown))
    window.open_document()

    path = tmp_path / "literal.txt"
    path.write_text("# Heading **literal**", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    assert window.editor.toPlainText() == "# Heading **literal**"
    assert window.style_selector.currentText() == "Paragraph"
    assert not window.editor.document().isModified()
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
    type_text(window, " text")
    assert window.save_document()
    assert path.read_text(encoding="utf-8") == "# Heading **literal** text"
    assert not window.editor.document().isModified()


@pytest.mark.parametrize(
    ("selected_filter", "extension", "contents"),
    [("", ".md", "# Heading\n\n"), ("Text (*.txt)", ".txt", "Heading")],
)
def test_extensionless_first_save_uses_document_or_explicit_text_choice(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected_filter: str,
    extension: str,
    contents: str,
) -> None:
    type_text(window, "Heading")
    window.style_selector.setCurrentIndex(1)
    filename = tmp_path / "new document"

    def selected(*_args: object) -> tuple[str, str]:
        return str(filename), selected_filter

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    assert window.current_path == filename.with_suffix(extension)
    assert filename.with_suffix(extension).read_text(encoding="utf-8") == contents


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
    assert old_path.read_text(encoding="utf-8") == "Old draft\n\n"
    assert window.editor.toPlainText() == "Next document"
    assert window.current_path == next_path
    assert not window.editor.document().isModified()


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
    window.editor.moveCursor(QTextCursor.MoveOperation.End)
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


@pytest.mark.parametrize(
    "text",
    (
        "  Leading text",
        "First\n  Second",
        "First\n",
        "First\n\n",
        "First\n\nSecond",
        "First\n   \nSecond",
        "  ",
        "First\n   ",
        "First\n\n\nSecond",
        "\n\nFirst",
        "  \u2063\u2063 text",
    ),
)
def test_typed_paragraph_whitespace_survives_real_save_and_reopen(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str
) -> None:
    def unexpected_error(_parent: object, _title: str, message: str) -> None:
        pytest.fail(message)

    monkeypatch.setattr(QMessageBox, "critical", unexpected_error)
    for index, line in enumerate(text.split("\n")):
        if index:
            QTest.keyClick(window.editor, Qt.Key.Key_Return)
        if "\u2063" in line:
            window.editor.insertPlainText(line)
        else:
            type_text(window, line)
    assert window.editor.toPlainText() == text
    before_blocks = [
        window.editor.document().findBlockByNumber(index).text()
        for index in range(window.editor.document().blockCount())
    ]
    path = tmp_path / "writing.md"
    save_to(monkeypatch, str(path))
    document = window.editor.document()
    undo_steps = document.availableUndoSteps()
    cursor_position = window.editor.textCursor().position()
    assert window.save_document()
    assert not document.isModified()
    assert document.availableUndoSteps() == undo_steps
    assert window.editor.textCursor().position() == cursor_position

    window.new_document()
    open_from(monkeypatch, str(path))
    window.open_document()
    assert window.editor.toPlainText() == text
    assert [
        window.editor.document().findBlockByNumber(index).text()
        for index in range(window.editor.document().blockCount())
    ] == before_blocks
    assert not window.editor.document().isModified()


@pytest.mark.parametrize(
    ("heading", "action_names"),
    [
        (1, ()),
        (0, ("bullet_action",)),
        (0, ("numbered_action",)),
        (0, ("quote_action", "numbered_action")),
        (0, ("quote_action",)),
    ],
)
def test_trailing_empty_structured_block_keeps_semantics_on_reopen(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    heading: int,
    action_names: tuple[str, ...],
) -> None:
    def unexpected_error(_parent: object, _title: str, message: str) -> None:
        pytest.fail(message)

    monkeypatch.setattr(QMessageBox, "critical", unexpected_error)
    if heading:
        window.style_selector.setCurrentIndex(heading)
    for name in action_names:
        getattr(window, name).trigger()
    type_text(window, "Item")
    QTest.keyClick(window.editor, Qt.Key.Key_Return)

    def block_state() -> list[tuple[str, int, object, bool]]:
        document = window.editor.document()
        states: list[tuple[str, int, object, bool]] = []
        for index in range(document.blockCount()):
            block = document.findBlockByNumber(index)
            text_list = block.textList()
            states.append(
                (
                    block.text(),
                    block.blockFormat().headingLevel(),
                    text_list.format().style() if text_list else None,
                    block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1,
                )
            )
        return states

    before = block_state()
    assert len(before) == 2 and before[1][0] == ""
    path = tmp_path / "structured.md"
    save_to(monkeypatch, str(path))
    assert window.save_document()
    window.new_document()
    open_from(monkeypatch, str(path))
    window.open_document()
    assert block_state() == before


def test_external_invisible_separator_is_not_decoded_without_ezmd_header(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_error(_parent: object, _title: str, message: str) -> None:
        pytest.fail(message)

    monkeypatch.setattr(QMessageBox, "critical", unexpected_error)
    path = tmp_path / "external.md"
    path.write_text("Before\u2063After\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    assert window.editor.document().firstBlock().text() == "Before\u2063After"
    assert window.save_document()
    window.new_document()
    window.open_document()
    assert window.editor.document().firstBlock().text() == "Before\u2063After"


def test_plain_text_save_does_not_validate_markdown(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "literal.txt"
    path.write_text("Old", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    type_text(window, " draft")

    def unexpected_conversion(*_args: object) -> None:
        pytest.fail("Plain text Save must not convert Markdown")

    monkeypatch.setattr(QTextDocument, "toMarkdown", unexpected_conversion)
    monkeypatch.setattr(QTextDocument, "setMarkdown", unexpected_conversion)
    assert window.save_document()
    assert path.read_text(encoding="utf-8") == " draftOld"


def test_failed_semantic_validation_does_not_change_live_formatting(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "heading.md"
    path.write_text("# Heading\n", encoding="utf-8")
    open_from(monkeypatch, str(path))
    window.open_document()
    document = window.editor.document()
    cursor = window.editor.textCursor()
    block_format = cursor.blockFormat()
    block_format.setProperty(QTextFormat.Property.BlockQuoteLevel, 1)
    cursor.setBlockFormat(block_format)  # An external Qt edit can create an unsafe heading + quote.
    assert document.firstBlock().blockFormat().headingLevel() == 1
    assert document.firstBlock().blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1
    before = (
        document.availableUndoSteps(),
        document.isModified(),
        window.editor.textCursor().position(),
    )
    errors: list[str] = []
    record_error(monkeypatch, errors)

    assert not window.save_document()
    assert errors and "formatting" in errors[0]
    assert path.read_text(encoding="utf-8") == "# Heading\n"
    assert window.editor.document() is document
    assert document.firstBlock().blockFormat().headingLevel() == 1
    assert document.firstBlock().blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1
    assert (
        document.availableUndoSteps(),
        document.isModified(),
        window.editor.textCursor().position(),
    ) == before
    assert window.current_path == path


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
    for name in PROFILES:
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
    for name in ("QTemp", "Lab", "Compact", "Focus"):
        window.profile_actions[name].trigger()
        assert window.editor.toPlainText() == after_undo
        assert document.isModified() == modified
        assert document.availableUndoSteps() == undo_steps
        assert document.isRedoAvailable()
    window.editor.redo()
    assert window.editor.toPlainText() == before


def test_compact_profile_uses_template_geometry(window: MainWindow) -> None:
    compact = PROFILES["Compact"]
    assert (
        compact.toolbar_gap,
        compact.toolbar_padding,
        compact.content_margin,
        compact.control_height,
        compact.control_padding,
        compact.control_radius,
        compact.editor_radius,
        compact.editor_padding,
        compact.border_width,
    ) == (6, 6, 20, 30, 8, 4, 6, 12, 1)
    window.profile_actions["Compact"].trigger()
    assert window.content_layout.contentsMargins().left() == 20
    assert "min-height: 30px" in window.toolbar.styleSheet()
    assert "border-radius: 6px" in window.editor.styleSheet()


def test_builtin_color_themes_switch_without_editing_the_document(window: MainWindow) -> None:
    assert window.theme_actions[DEFAULT_THEME].isChecked()
    assert not window.theme_actions["Light"].isChecked()
    window.editor.setPlainText("Writing")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    window.editor.setTextCursor(cursor)
    window.bold_action.trigger()
    document = window.editor.document()
    before = (
        window.editor.toPlainText(),
        document.availableUndoSteps(),
        document.isModified(),
        window.editor.textCursor().anchor(),
        window.editor.textCursor().position(),
        window.bold_action.isChecked(),
    )
    window.profile_actions["Compact"].trigger()
    for name in ("Light", "Dark", "Light"):
        window.theme_actions[name].trigger()
        colors = THEMES[name]
        assert window.theme_actions[name].isChecked()
        assert sum(action.isChecked() for action in window.theme_actions.values()) == 1
        assert window.profile_actions["Compact"].isChecked()
        palette = window.palette()
        assert palette.color(QPalette.ColorRole.Window).name().upper() == colors.background
        assert palette.color(QPalette.ColorRole.Base).name().upper() == colors.surface
        assert palette.color(QPalette.ColorRole.Highlight).name().upper() == colors.selection
        assert (
            palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text).name().upper()
            == colors.text_muted
        )
        assert colors.background_elevated in window.toolbar.styleSheet()
        assert colors.surface_active in window.toolbar.styleSheet()
        assert colors.surface_alternate in window.style_selector.styleSheet()
        assert colors.selection in window.editor.styleSheet()
        assert (
            window.editor.toPlainText(),
            document.availableUndoSteps(),
            document.isModified(),
            window.editor.textCursor().anchor(),
            window.editor.textCursor().position(),
            window.bold_action.isChecked(),
        ) == before
    window.undo_action.trigger()
    assert not window.bold_action.isChecked()
    window.redo_action.trigger()
    assert window.bold_action.isChecked()


def test_focus_and_compact_buttons_are_quiet_at_rest_while_other_profiles_retain_boundaries(
    window: MainWindow,
) -> None:
    assert PROFILES["Focus"].quiet_buttons_at_rest
    assert PROFILES["Compact"].quiet_buttons_at_rest
    assert not PROFILES["Lab"].quiet_buttons_at_rest
    assert not PROFILES["QTemp"].quiet_buttons_at_rest

    for name in PROFILES:
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
