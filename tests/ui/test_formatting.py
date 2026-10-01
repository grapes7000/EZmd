"""User-visible formatting of the one native Qt document."""

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import (
    QFont,
    QKeySequence,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
    QTextListFormat,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QToolButton
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow
from ezmd.ui.visual_profiles import _resolve_base_point_size, heading_point_size


@pytest.fixture
def window(qtbot: QtBot) -> Iterator[MainWindow]:
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setFocus()
    yield window


def select(window: MainWindow, start: int, end: int) -> None:
    cursor = window.editor.textCursor()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)


def char_format(window: MainWindow, position: int) -> QTextCharFormat:
    cursor = QTextCursor(window.editor.document())
    cursor.setPosition(position + 1)
    return cursor.charFormat()


def headings(window: MainWindow) -> list[int]:
    document = window.editor.document()
    return [
        document.findBlockByNumber(i).blockFormat().headingLevel()
        for i in range(document.blockCount())
    ]


def list_styles(window: MainWindow) -> list[QTextListFormat.Style | None]:
    document = window.editor.document()
    styles: list[QTextListFormat.Style | None] = []
    for i in range(document.blockCount()):
        text_list = document.findBlockByNumber(i).textList()
        styles.append(text_list.format().style() if text_list else None)
    return styles


def quote_levels(window: MainWindow) -> list[int | None]:
    document = window.editor.document()
    return [
        document.findBlockByNumber(i).blockFormat().property(QTextFormat.Property.BlockQuoteLevel)
        for i in range(document.blockCount())
    ]


def structure(window: MainWindow) -> tuple[int, QTextListFormat.Style | None, int | None, int]:
    block = window.editor.document().begin()
    text_list = block.textList()
    return (
        block.blockFormat().headingLevel(),
        text_list.format().style() if text_list else None,
        block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel),
        block.blockFormat().indent(),
    )


def test_toolbar_groups_and_curved_undo_controls(window: MainWindow) -> None:
    actions = window.toolbar.actions()
    assert actions[0:2] == [window.undo_action, window.redo_action]
    assert actions[2].isSeparator()
    assert window.toolbar.widgetForAction(actions[3]) is window.style_selector
    assert actions[4].isSeparator()
    assert actions[5:8] == [window.bold_action, window.italic_action, window.strike_action]
    assert actions[8].isSeparator()
    assert actions[9:] == [window.bullet_action, window.numbered_action, window.quote_action]
    assert [window.style_selector.itemText(i) for i in range(window.style_selector.count())] == [
        "Paragraph",
        "H1",
        "H2",
        "H3",
    ]
    for action, glyph, name in (
        (window.undo_action, "↶", "Undo"),
        (window.redo_action, "↷", "Redo"),
    ):
        button = window.toolbar.widgetForAction(action)
        assert isinstance(button, QToolButton)
        assert button.text() == glyph
        assert button.accessibleName() == name
        assert button.toolTip() == name
    QTest.keyClicks(window.editor, "Draft")
    undo_button = window.toolbar.widgetForAction(window.undo_action)
    assert isinstance(undo_button, QToolButton)
    assert undo_button.text() == "↶"
    window.undo_action.trigger()
    redo_button = window.toolbar.widgetForAction(window.redo_action)
    assert isinstance(redo_button, QToolButton)
    assert redo_button.text() == "↷"


@pytest.mark.parametrize(
    ("action_name", "attribute", "active_value"),
    [
        ("bold_action", "fontWeight", QFont.Weight.Bold),
        ("italic_action", "fontItalic", True),
        ("strike_action", "fontStrikeOut", True),
    ],
)
def test_character_action_formats_selection_toggles_and_undoes_in_one_step(
    window: MainWindow, action_name: str, attribute: str, active_value: object
) -> None:
    window.editor.setPlainText("first second")
    select(window, 0, 5)
    action = getattr(window, action_name)
    document = window.editor.document()
    before = document.availableUndoSteps()
    action.trigger()
    assert getattr(char_format(window, 2), attribute)() == active_value
    assert document.availableUndoSteps() > before
    window.undo_action.trigger()
    assert not action.isChecked()
    assert document.availableUndoSteps() == before
    assert window.editor.toPlainText() == "first second"
    window.redo_action.trigger()
    assert action.isChecked()
    select(window, 0, 5)
    action.trigger()
    assert not action.isChecked()
    assert getattr(char_format(window, 2), attribute)() != active_value


@pytest.mark.parametrize("action_name", ["bold_action", "italic_action", "strike_action"])
def test_character_action_changes_future_typing_without_editing_existing_text(
    window: MainWindow, action_name: str
) -> None:
    window.editor.setPlainText("ab")
    select(window, 1, 1)
    action = getattr(window, action_name)
    document = window.editor.document()
    document.setModified(False)
    steps = document.availableUndoSteps()
    action.trigger()
    assert not document.isModified()
    assert document.availableUndoSteps() == steps
    QTest.keyClicks(window.editor, "X")
    assert window.editor.toPlainText() == "aXb"
    assert action.isChecked()
    action.trigger()
    QTest.keyClicks(window.editor, "Y")
    assert window.editor.toPlainText() == "aXYb"
    assert not action.isChecked()
    attribute = {
        "bold_action": "fontWeight",
        "italic_action": "fontItalic",
        "strike_action": "fontStrikeOut",
    }[action_name]
    assert (
        getattr(char_format(window, 1), attribute)() != getattr(char_format(window, 2), attribute)()
    )


@pytest.mark.parametrize("action_name", ["bold_action", "italic_action", "strike_action"])
def test_mixed_character_selection_becomes_fully_formatted(
    window: MainWindow, action_name: str
) -> None:
    window.editor.setPlainText("one two")
    action = getattr(window, action_name)
    select(window, 0, 3)
    action.trigger()
    select(window, 0, 7)
    assert not action.isChecked()
    action.trigger()
    assert action.isChecked()
    select(window, 4, 7)
    assert action.isChecked()


def test_clicking_toolbar_format_keeps_selection_and_typing_focus(window: MainWindow) -> None:
    window.editor.setPlainText("write here")
    select(window, 0, 5)
    button = window.toolbar.widgetForAction(window.bold_action)
    assert isinstance(button, QToolButton)
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
    assert window.editor.textCursor().selectedText() == "write"
    assert window.editor.hasFocus()
    assert window.bold_action.isChecked()
    select(window, 5, 5)
    QTest.keyClicks(window.editor, "!")
    assert window.editor.toPlainText() == "write! here"


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_paragraph_style_applies_to_whole_blocks_and_preserves_inline_emphasis(
    window: MainWindow, level: int
) -> None:
    window.editor.setPlainText("one\ntwo\nthree")
    select(window, 0, 3)
    window.bold_action.trigger()
    window.italic_action.trigger()
    select(window, 5, 5)
    window.style_selector.setCurrentIndex(1)
    select(window, 1, 7)
    assert window.style_selector.currentIndex() == -1
    steps = window.editor.document().availableUndoSteps()
    window.style_selector.setCurrentIndex(level)
    assert headings(window) == [level, level, 0]
    assert window.style_selector.currentIndex() == level
    window.undo_action.trigger()
    assert headings(window) == [0, 1, 0]
    assert window.editor.document().availableUndoSteps() == steps
    window.redo_action.trigger()
    assert headings(window) == [level, level, 0]
    select(window, 1, 1)
    assert window.bold_action.isChecked()
    assert window.italic_action.isChecked()


def test_heading_presentation_does_not_imply_inline_bold_or_italic(window: MainWindow) -> None:
    window.editor.setPlainText("Heading\nBody")
    for level in (1, 2, 3, 0):
        select(window, 2, 2)
        window.style_selector.setCurrentIndex(level)
        assert headings(window) == [level, 0]
        assert not window.bold_action.isChecked()
        assert not window.italic_action.isChecked()
        assert char_format(window, 2).fontWeight() == QFont.Weight.Normal
        assert not char_format(window, 2).fontItalic()


def test_new_heading_styles_text_typed_into_an_empty_block(window: MainWindow) -> None:
    window.style_selector.setCurrentIndex(1)
    assert headings(window) == [1]
    QTest.keyClicks(window.editor, "Title")
    assert headings(window) == [1]
    assert not window.bold_action.isChecked()
    assert char_format(window, 1).fontPointSize() > 0


def test_heading_size_falls_back_when_a_font_has_no_usable_size(window: MainWindow) -> None:
    font_without_size = QFont()
    assert font_without_size.pointSizeF() <= 0
    assert font_without_size.pixelSize() <= 0
    assert _resolve_base_point_size((font_without_size,), window.editor.logicalDpiY()) > 0


@pytest.mark.parametrize("level", [1, 2, 3])
@pytest.mark.parametrize("one_by_one", [False, True])
def test_heading_keeps_typing_size_after_deleting_all_text(
    window: MainWindow, level: int, one_by_one: bool
) -> None:
    window.style_selector.setCurrentIndex(level)
    QTest.keyClicks(window.editor, "Title")
    if one_by_one:
        for _ in range(5):
            QTest.keyClick(window.editor, Qt.Key.Key_Backspace)
    else:
        select(window, 0, 5)
        QTest.keyClick(window.editor, Qt.Key.Key_Delete)
    assert window.editor.toPlainText() == ""
    assert headings(window) == [level]
    assert window.style_selector.currentIndex() == level

    QTest.keyClicks(window.editor, "Again")
    assert headings(window) == [level]
    assert window.style_selector.currentIndex() == level
    assert char_format(window, 1).fontPointSize() == pytest.approx(
        heading_point_size(window.editor, level)
    )
    if not one_by_one:
        window.undo_action.trigger()
        assert window.editor.toPlainText() == ""
        window.undo_action.trigger()
        assert window.editor.toPlainText() == "Title"
        window.redo_action.trigger()
        window.redo_action.trigger()
        assert window.editor.toPlainText() == "Again"
        assert char_format(window, 1).fontPointSize() == pytest.approx(
            heading_point_size(window.editor, level)
        )


@pytest.mark.parametrize(
    ("first", "second"),
    [
        (QTextListFormat.Style.ListDisc, QTextListFormat.Style.ListDecimal),
        (QTextListFormat.Style.ListDecimal, QTextListFormat.Style.ListDisc),
    ],
)
def test_real_lists_toggle_and_convert_without_nested_or_literal_markers(
    window: MainWindow, first: QTextListFormat.Style, second: QTextListFormat.Style
) -> None:
    window.editor.setPlainText("one\ntwo\nthree")
    select(window, 0, 7)
    actions = {
        QTextListFormat.Style.ListDisc: window.bullet_action,
        QTextListFormat.Style.ListDecimal: window.numbered_action,
    }
    actions[first].trigger()
    assert list_styles(window) == [first, first, None]
    actions[second].trigger()
    assert list_styles(window) == [second, second, None]
    assert window.editor.toPlainText() == "one\ntwo\nthree"
    window.undo_action.trigger()
    assert list_styles(window) == [first, first, None]
    window.redo_action.trigger()
    select(window, 0, 7)
    actions[second].trigger()
    assert list_styles(window) == [None, None, None]


def test_mixed_list_selection_converts_only_affected_blocks(window: MainWindow) -> None:
    window.editor.setPlainText("one\ntwo\nthree")
    select(window, 0, 7)
    window.bullet_action.trigger()
    select(window, 4, 10)
    window.numbered_action.trigger()
    assert list_styles(window) == [
        QTextListFormat.Style.ListDisc,
        QTextListFormat.Style.ListDecimal,
        QTextListFormat.Style.ListDecimal,
    ]
    window.undo_action.trigger()
    assert list_styles(window) == [
        QTextListFormat.Style.ListDisc,
        QTextListFormat.Style.ListDisc,
        None,
    ]


@pytest.mark.parametrize("action_name", ["bullet_action", "numbered_action"])
def test_list_enter_and_backspace_reapply_remains_top_level(
    window: MainWindow, action_name: str
) -> None:
    window.editor.setPlainText("item")
    action = getattr(window, action_name)
    action.trigger()
    first = window.editor.document().begin().textList()
    assert first
    top_level_indent = first.format().indent()
    style = first.format().style()
    assert window.editor.document().begin().blockFormat().indent() == 0

    for _ in range(3):
        select(window, 0, 0)
        QTest.keyClick(window.editor, Qt.Key.Key_Backspace)
        assert list_styles(window) == [None]
        action.trigger()
        block = window.editor.document().begin()
        assert block.textList()
        assert block.textList().format().indent() == top_level_indent
        assert block.blockFormat().indent() == 0

    select(window, 4, 4)
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    assert list_styles(window) == [style, style]
    assert window.editor.document().lastBlock().blockFormat().indent() == 0


@pytest.mark.parametrize(
    "names",
    [
        ("quote_action", "bullet_action", "quote_action", "bullet_action"),
        ("bullet_action", "quote_action", "bullet_action", "quote_action"),
        ("quote_action", "numbered_action", "quote_action", "numbered_action"),
        ("numbered_action", "quote_action", "numbered_action", "quote_action"),
    ],
)
def test_quote_list_conversions_are_exclusive_normalized_and_one_undo_step(
    window: MainWindow, names: tuple[str, ...]
) -> None:
    window.editor.setPlainText("item")
    for name in names:
        before = structure(window)
        getattr(window, name).trigger()
        after = structure(window)
        assert after != before
        assert window.editor.toPlainText() == "item"
        if name == "quote_action":
            assert after == (0, None, 1, 1)
            assert window.quote_action.isChecked()
            assert not window.bullet_action.isChecked()
            assert not window.numbered_action.isChecked()
        else:
            style = (
                QTextListFormat.Style.ListDisc
                if name == "bullet_action"
                else QTextListFormat.Style.ListDecimal
            )
            assert after == (0, style, None, 0)
            assert window.editor.document().begin().textList().format().indent() == 1
            assert not window.quote_action.isChecked()
            assert getattr(window, name).isChecked()
        window.undo_action.trigger()
        assert structure(window) == before
        window.redo_action.trigger()
        assert structure(window) == after


def test_selected_quote_blocks_convert_to_one_top_level_list_undo_step(
    window: MainWindow,
) -> None:
    window.editor.setPlainText("one\ntwo\nthree")
    select(window, 0, 7)
    window.quote_action.trigger()
    window.numbered_action.trigger()
    assert list_styles(window) == [QTextListFormat.Style.ListDecimal] * 2 + [None]
    assert quote_levels(window) == [None, None, None]
    assert [
        window.editor.document().findBlockByNumber(i).blockFormat().indent() for i in (0, 1)
    ] == [0, 0]
    window.undo_action.trigger()
    assert quote_levels(window) == [1, 1, None]
    assert list_styles(window) == [None, None, None]
    window.redo_action.trigger()
    assert list_styles(window) == [QTextListFormat.Style.ListDecimal] * 2 + [None]


@pytest.mark.parametrize("level", [1, 2, 3])
@pytest.mark.parametrize("action_name", ["quote_action", "bullet_action", "numbered_action"])
def test_heading_survives_structural_application_and_removal(
    window: MainWindow, level: int, action_name: str
) -> None:
    window.editor.setPlainText("Heading")
    window.style_selector.setCurrentIndex(level)
    before_size = char_format(window, 1).fontPointSize()
    action = getattr(window, action_name)
    action.trigger()
    assert headings(window) == [level]
    assert char_format(window, 1).fontPointSize() == before_size
    assert window.style_selector.currentIndex() == level
    action.trigger()
    assert structure(window) == (level, None, None, 0)
    assert char_format(window, 1).fontPointSize() == before_size
    assert window.style_selector.currentIndex() == level


@pytest.mark.parametrize("level", [1, 2, 3])
@pytest.mark.parametrize(
    ("action_name", "style"),
    [
        ("bullet_action", QTextListFormat.Style.ListDisc),
        ("numbered_action", QTextListFormat.Style.ListDecimal),
    ],
)
def test_heading_list_marker_uses_heading_typography_and_list_removal_keeps_heading(
    window: MainWindow, level: int, action_name: str, style: QTextListFormat.Style
) -> None:
    window.editor.setPlainText("Heading")
    window.style_selector.setCurrentIndex(level)
    action = getattr(window, action_name)
    action.trigger()
    block = window.editor.document().begin()
    expected_size = heading_point_size(window.editor, level)
    assert block.blockFormat().headingLevel() == level
    assert list_styles(window) == [style]
    # Qt draws native list markers with the block character format, not text fragments.
    assert block.charFormat().fontPointSize() == pytest.approx(expected_size)
    assert char_format(window, 1).fontPointSize() == pytest.approx(expected_size)
    assert window.editor.toPlainText() == "Heading"

    action.trigger()
    assert headings(window) == [level]
    assert list_styles(window) == [None]
    assert block.charFormat().fontPointSize() == pytest.approx(expected_size)
    window.undo_action.trigger()
    assert list_styles(window) == [style]
    assert block.charFormat().fontPointSize() == pytest.approx(expected_size)
    window.redo_action.trigger()
    assert list_styles(window) == [None]
    assert headings(window) == [level]


@pytest.mark.parametrize("action_name", ["bullet_action", "numbered_action"])
def test_changing_heading_in_list_keeps_native_list_and_undo_history(
    window: MainWindow, action_name: str
) -> None:
    window.editor.setPlainText("Title")
    getattr(window, action_name).trigger()
    style = list_styles(window)
    for level in (1, 3, 0, 2):
        window.style_selector.setCurrentIndex(level)
        block = window.editor.document().begin()
        assert headings(window) == [level]
        assert list_styles(window) == style
        assert block.charFormat().fontPointSize() == pytest.approx(
            heading_point_size(window.editor, level)
        )
    window.undo_action.trigger()
    assert headings(window) == [0]
    assert list_styles(window) == style
    window.redo_action.trigger()
    assert headings(window) == [2]
    assert list_styles(window) == style


@pytest.mark.parametrize("action_name", ["bullet_action", "numbered_action"])
def test_retyping_empty_heading_list_keeps_text_and_marker_typography(
    window: MainWindow, action_name: str
) -> None:
    window.style_selector.setCurrentIndex(1)
    getattr(window, action_name).trigger()
    QTest.keyClicks(window.editor, "Title")
    select(window, 0, 5)
    QTest.keyClick(window.editor, Qt.Key.Key_Delete)
    assert headings(window) == [1]
    assert list_styles(window)[0] is not None
    QTest.keyClicks(window.editor, "Again")
    block = window.editor.document().begin()
    expected_size = heading_point_size(window.editor, 1)
    assert char_format(window, 1).fontPointSize() == pytest.approx(expected_size)
    assert block.charFormat().fontPointSize() == pytest.approx(expected_size)


def test_profile_switch_keeps_heading_list_typography_and_history(window: MainWindow) -> None:
    window.editor.setPlainText("Title")
    window.style_selector.setCurrentIndex(2)
    window.numbered_action.trigger()
    document = window.editor.document()
    document.setModified(False)
    cursor = window.editor.textCursor()
    before = (
        window.editor.toPlainText(),
        cursor.anchor(),
        cursor.position(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        window.current_path,
        document.begin().charFormat().fontPointSize(),
    )
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        cursor = window.editor.textCursor()
        assert (
            window.editor.toPlainText(),
            cursor.anchor(),
            cursor.position(),
            document.availableUndoSteps(),
            document.isRedoAvailable(),
            window.current_path,
            document.begin().charFormat().fontPointSize(),
        ) == before
        assert headings(window) == [2]
        assert list_styles(window) == [QTextListFormat.Style.ListDecimal]
        assert not document.isModified()
    window.undo_action.trigger()
    assert headings(window) == [2]
    assert list_styles(window) == [None]
    window.redo_action.trigger()
    assert list_styles(window) == [QTextListFormat.Style.ListDecimal]


def test_repeated_undo_redo_restores_text_structure_inline_format_and_toolbar(
    window: MainWindow,
) -> None:
    window.editor.setPlainText("one")
    select(window, 0, 3)
    window.bold_action.trigger()
    select(window, 1, 1)
    window.style_selector.setCurrentIndex(2)
    window.quote_action.trigger()
    window.bullet_action.trigger()
    expected = ("one", (2, QTextListFormat.Style.ListDisc, None, 0), True, "H2")

    def snapshot() -> tuple[
        str, tuple[int, QTextListFormat.Style | None, int | None, int], bool, str
    ]:
        select(window, 1, 1)
        return (
            window.editor.toPlainText(),
            structure(window),
            window.bold_action.isChecked(),
            window.style_selector.currentText(),
        )

    assert snapshot() == expected
    for _ in range(3):
        window.undo_action.trigger()
        assert structure(window) == (2, None, 1, 1)
        assert window.quote_action.isChecked()
        window.undo_action.trigger()
        assert structure(window) == (2, None, None, 0)
        window.undo_action.trigger()
        assert structure(window) == (0, None, None, 0)
        window.undo_action.trigger()
        assert snapshot() == ("one", (0, None, None, 0), False, "Paragraph")
        for _ in range(4):
            window.redo_action.trigger()
        assert snapshot() == expected


def test_quote_uses_builtin_top_level_property_and_toggles_selected_blocks(
    window: MainWindow,
) -> None:
    window.editor.setPlainText("one\ntwo\nthree")
    select(window, 0, 1)
    window.quote_action.trigger()
    assert quote_levels(window) == [1, None, None]
    select(window, 0, 7)
    assert not window.quote_action.isChecked()
    window.quote_action.trigger()
    assert quote_levels(window) == [1, 1, None]
    assert window.quote_action.isChecked()
    window.undo_action.trigger()
    assert quote_levels(window) == [1, None, None]
    window.redo_action.trigger()
    select(window, 0, 7)
    window.quote_action.trigger()
    assert quote_levels(window) == [None, None, None]
    assert window.editor.toPlainText() == "one\ntwo\nthree"


def test_quote_enters_and_exits_without_changing_heading_or_inline_typography(
    window: MainWindow,
) -> None:
    window.editor.setPlainText("Heading")
    window.style_selector.setCurrentIndex(2)
    select(window, 0, 7)
    for action in (window.bold_action, window.italic_action, window.strike_action):
        action.trigger()
    window.quote_action.trigger()
    before = char_format(window, 1)
    assert headings(window) == [2]
    assert quote_levels(window) == [1]
    select(window, 7, 7)
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    assert quote_levels(window) == [1, 1]
    assert window.editor.toPlainText() == "Heading\n"
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    assert quote_levels(window) == [1, None]
    assert window.editor.toPlainText() == "Heading\n"
    assert headings(window)[0] == 2
    after = char_format(window, 1)
    assert after.fontPointSize() == before.fontPointSize()
    assert after.fontWeight() == before.fontWeight()
    assert after.fontItalic() == before.fontItalic()
    assert after.fontStrikeOut() == before.fontStrikeOut()


def test_quote_rail_paint_and_profile_switch_are_document_read_only(window: MainWindow) -> None:
    window.editor.setPlainText("Intro\nQuoted writing\nMore quoted writing\nEnd")
    select(window, 6, 38)
    window.quote_action.trigger()
    assert quote_levels(window) == [None, 1, 1, None]
    document = window.editor.document()
    document.setModified(False)
    before = (
        window.editor.toPlainText(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
        window.editor.textCursor().anchor(),
        window.editor.textCursor().position(),
        window.current_path,
    )
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        assert not window.editor.viewport().grab().isNull()
        assert quote_levels(window) == [None, 1, 1, None]
        assert (
            window.editor.toPlainText(),
            document.availableUndoSteps(),
            document.isRedoAvailable(),
            window.editor.textCursor().anchor(),
            window.editor.textCursor().position(),
            window.current_path,
        ) == before
        assert not document.isModified()
    window.quote_action.trigger()
    assert quote_levels(window) == [None, None, None, None]
    assert not window.editor.viewport().grab().isNull()
    assert window.editor.toPlainText() == before[0]
    window.undo_action.trigger()
    assert quote_levels(window) == [None, 1, 1, None]


def test_cursor_sync_is_read_only_and_profiles_preserve_rich_history(window: MainWindow) -> None:
    window.editor.setPlainText("first\nsecond")
    select(window, 0, 5)
    window.bold_action.trigger()
    select(window, 0, 0)
    window.style_selector.setCurrentIndex(2)
    window.bullet_action.trigger()
    window.quote_action.trigger()
    document = window.editor.document()
    document.setModified(False)
    path = window.current_path
    before = (
        window.editor.toPlainText(),
        document.availableUndoSteps(),
        document.isRedoAvailable(),
    )
    select(window, 7, 7)
    assert not window.bold_action.isChecked()
    assert not window.bullet_action.isChecked()
    select(window, 2, 2)
    assert window.bold_action.isChecked()
    assert window.style_selector.currentText() == "H2"
    assert not window.bullet_action.isChecked()
    assert window.quote_action.isChecked()
    cursor = window.editor.textCursor()
    position = (cursor.anchor(), cursor.position())
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        assert window.profile_actions[name].isChecked()
        assert (
            window.editor.textCursor().anchor(),
            window.editor.textCursor().position(),
        ) == position
        assert (
            window.editor.toPlainText(),
            document.availableUndoSteps(),
            document.isRedoAvailable(),
        ) == before
        assert not document.isModified()
        assert window.current_path == path
        assert headings(window)[0] == 2
        assert quote_levels(window)[0] == 1
    window.undo_action.trigger()
    assert quote_levels(window)[0] is None
    assert list_styles(window)[0] == QTextListFormat.Style.ListDisc
    window.profile_actions["Lab"].trigger()
    assert document.isRedoAvailable()
    window.redo_action.trigger()
    assert quote_levels(window)[0] == 1


@pytest.mark.parametrize(
    ("standard", "action_name"),
    [
        (QKeySequence.StandardKey.Bold, "bold_action"),
        (QKeySequence.StandardKey.Italic, "italic_action"),
    ],
)
def test_standard_shortcuts_format_text(
    window: MainWindow, standard: QKeySequence.StandardKey, action_name: str
) -> None:
    window.editor.setPlainText("Some text")
    select(window, 0, 4)
    QTest.keySequence(window.editor, QKeySequence(standard))
    assert getattr(window, action_name).isChecked()


def test_standard_undo_redo_shortcuts_use_the_document_history(window: MainWindow) -> None:
    QTest.keyClicks(window.editor, "text")
    QTest.keySequence(window.editor, QKeySequence(QKeySequence.StandardKey.Undo))
    assert window.editor.toPlainText() != "text"
    QTest.keySequence(window.editor, QKeySequence(QKeySequence.StandardKey.Redo))
    assert window.editor.toPlainText() == "text"


def test_rich_html_paste_stays_plain_even_after_formatting(window: MainWindow) -> None:
    data = QMimeData()
    data.setHtml("<h1><em>External</em></h1>")
    data.setText("External")
    window.editor.insertFromMimeData(data)
    assert window.editor.toPlainText() == "External"
    assert headings(window) == [0]
    assert not window.italic_action.isChecked()
    assert not window.bold_action.isChecked()


def test_strikethrough_toolbar_glyph_is_struck_without_losing_accessibility(
    window: MainWindow,
) -> None:
    button = window.toolbar.widgetForAction(window.strike_action)
    assert isinstance(button, QToolButton)
    assert button.text() == "S"
    assert button.font().strikeOut()
    assert button.accessibleName() == "Strikethrough"
    assert button.toolTip() == "Strikethrough"
    for name in ("Lab", "QTemp", "Focus"):
        window.profile_actions[name].trigger()
        assert button.font().strikeOut()
    select(window, 0, 0)
    window.strike_action.trigger()
    QTest.keyClicks(window.editor, "test")
    assert char_format(window, 1).fontStrikeOut()
