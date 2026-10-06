"""Supported formatting states through real toolbar, Save, and Open workflows."""

from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor, QTextFormat, QTextListFormat
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QFileDialog, QMessageBox
from pytestqt.qtbot import QtBot

from ezmd.ui.main_window import MainWindow

HEADING_LEVELS = (0, 1, 2, 3)
LIST_STATES = ("none", "bullet", "numbered")
INLINE_STATES = tuple(
    (bold, italic, strike)
    for bold in (False, True)
    for italic in (False, True)
    for strike in (False, True)
)
PARAGRAPH_INLINE = (
    (False, False, False),
    (True, False, False),
    (False, True, False),
    (True, True, False),
    (False, False, True),
)
HEADING_INLINE = ((True, False, False),)
SAFE_STATES = (
    [(0, list_state, False, inline) for list_state in LIST_STATES for inline in PARAGRAPH_INLINE]
    + [(0, "none", True, inline) for inline in PARAGRAPH_INLINE]
    + [(heading, "none", False, inline) for heading in (1, 2, 3) for inline in HEADING_INLINE]
)
TEXT = "Sample writing"


@pytest.fixture
def window(qtbot: QtBot) -> Iterator[MainWindow]:
    window = MainWindow()
    qtbot.addWidget(
        window, before_close_func=lambda widget: widget.editor.document().setModified(False)
    )
    window.show()
    window.editor.setFocus()
    yield window


def create_typing_state(
    window: MainWindow,
    heading: int,
    list_state: str,
    quote: bool,
    inline: tuple[bool, bool, bool] = (False, False, False),
) -> None:
    window.style_selector.setCurrentIndex(heading)
    if list_state == "bullet":
        window.bullet_action.trigger()
    elif list_state == "numbered":
        window.numbered_action.trigger()
    if quote:
        window.quote_action.trigger()
    for enabled, action in zip(
        inline, (window.bold_action, window.italic_action, window.strike_action), strict=True
    ):
        if enabled and not action.isChecked():
            action.trigger()


def type_text(window: MainWindow, text: str = TEXT) -> None:
    QTest.keyClicks(window.editor, text)


def select_text(window: MainWindow) -> None:
    cursor = window.editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(len(TEXT), QTextCursor.MoveMode.KeepAnchor)
    window.editor.setTextCursor(cursor)


def inspect_block(window: MainWindow, index: int = 0) -> tuple[object, ...]:
    block = window.editor.document().findBlockByNumber(index)
    text_list = block.textList()
    list_style = text_list.format().style() if text_list else None
    fragments: list[tuple[bool, bool, bool]] = []
    fragment_it = block.begin()
    while not fragment_it.atEnd():
        fragment = fragment_it.fragment()
        if fragment.text():
            fmt = fragment.charFormat()
            fragments.append(
                (
                    fmt.fontWeight() >= QFont.Weight.Bold,
                    fmt.fontItalic(),
                    fmt.fontStrikeOut(),
                )
            )
        fragment_it += 1
    return (
        block.text(),
        block.blockFormat().headingLevel(),
        list_style,
        block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1,
        tuple(fragments),
    )


def expected_block(
    text: str, heading: int, list_state: str, quote: bool, inline: tuple[bool, bool, bool]
) -> tuple[object, ...]:
    list_style = {
        "none": None,
        "bullet": QTextListFormat.Style.ListDisc,
        "numbered": QTextListFormat.Style.ListDecimal,
    }[list_state]
    return (text, heading, list_style, quote, (inline,))


def inspect_toolbar(window: MainWindow) -> tuple[object, ...]:
    return (
        window.style_selector.currentIndex(),
        window.bullet_action.isChecked(),
        window.numbered_action.isChecked(),
        window.quote_action.isChecked(),
        window.bold_action.isChecked(),
        window.italic_action.isChecked(),
        window.strike_action.isChecked(),
    )


def expected_toolbar(
    heading: int, list_state: str, quote: bool, inline: tuple[bool, bool, bool]
) -> tuple[object, ...]:
    return (heading, list_state == "bullet", list_state == "numbered", quote, *inline)


def assert_live_state(
    window: MainWindow,
    text: str,
    heading: int,
    list_state: str,
    quote: bool,
    inline: tuple[bool, bool, bool] = (False, False, False),
    index: int = 0,
) -> None:
    document_state = inspect_block(window, index)
    toolbar_state = inspect_toolbar(window)
    expected_document = expected_block(text, heading, list_state, quote, inline)
    expected_controls = expected_toolbar(heading, list_state, quote, inline)
    assert (document_state, toolbar_state) == (expected_document, expected_controls), (
        f"document: {document_state!r} (expected {expected_document!r}); "
        f"toolbar: {toolbar_state!r} (expected {expected_controls!r})"
    )


def save_and_reopen(
    window: MainWindow, path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    def unexpected_error(_parent: object, _title: str, message: str) -> None:
        pytest.fail(message)

    monkeypatch.setattr(QMessageBox, "critical", unexpected_error)

    def selected(*_args: object) -> tuple[str, str]:
        return str(path), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", selected)
    assert window.save_document()
    after_save = inspect_block(window)
    window.new_document()
    monkeypatch.setattr(QFileDialog, "getOpenFileName", selected)
    window.open_document()
    reopened = inspect_block(window)
    # The insertion format at position zero may differ from the first text fragment.
    cursor = window.editor.textCursor()
    cursor.setPosition(1)
    window.editor.setTextCursor(cursor)
    return after_save, reopened


@pytest.mark.parametrize("heading", HEADING_LEVELS)
@pytest.mark.parametrize("list_state", LIST_STATES)
@pytest.mark.parametrize("quote", (False, True))
@pytest.mark.parametrize("inline", INLINE_STATES)
def test_every_requested_state_normalizes_to_a_safe_round_trip(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    heading: int,
    list_state: str,
    quote: bool,
    inline: tuple[bool, bool, bool],
) -> None:
    create_typing_state(window, heading, list_state, quote, inline)
    type_text(window)
    live = inspect_block(window)
    live_toolbar = inspect_toolbar(window)
    after_save, reopened = save_and_reopen(window, tmp_path / "state.md", monkeypatch)
    actual_heading = cast(int, live[1])
    actual_list = cast(QTextListFormat.Style | None, live[2])
    actual_quote = cast(bool, live[3])
    actual_inline = cast(tuple[tuple[bool, bool, bool], ...], live[4])
    assert live[0] == TEXT and len(actual_inline) == 1
    bold, italic, strike = actual_inline[0]
    assert not (actual_heading and actual_quote)
    assert not (actual_heading and actual_list is not None)
    assert not (actual_quote and actual_list is not None)
    assert not (actual_heading and (not bold or strike))
    assert not (strike and (bold or italic))
    controls = expected_toolbar(
        actual_heading,
        "bullet"
        if actual_list == QTextListFormat.Style.ListDisc
        else "numbered"
        if actual_list == QTextListFormat.Style.ListDecimal
        else "none",
        actual_quote,
        (bold, italic, strike),
    )
    assert (after_save, reopened, live_toolbar, inspect_toolbar(window)) == (
        live,
        live,
        controls,
        controls,
    )


@pytest.mark.parametrize(("heading", "list_state", "quote", "inline"), SAFE_STATES)
def test_every_supported_semantic_state_survives_real_save_and_reopen(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    heading: int,
    list_state: str,
    quote: bool,
    inline: tuple[bool, bool, bool],
) -> None:
    create_typing_state(window, heading, list_state, quote, inline)
    type_text(window)
    assert_live_state(window, TEXT, heading, list_state, quote, inline)
    after_save, reopened = save_and_reopen(window, tmp_path / "supported.md", monkeypatch)
    expected = expected_block(TEXT, heading, list_state, quote, inline)
    assert after_save == reopened == expected


@pytest.mark.parametrize("order", ("heading-then-list", "list-then-heading"))
@pytest.mark.parametrize("list_state", ("bullet", "numbered"))
def test_consecutive_heading_list_attempts_normalize_to_safe_blocks(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    list_state: str,
    order: str,
) -> None:
    create_typing_state(window, 1 if order == "heading-then-list" else 0, list_state, False)
    type_text(window, "First")
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    type_text(window, "Second")
    if order == "list-then-heading":
        cursor = window.editor.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(len("First\nSecond"), QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        window.style_selector.setCurrentIndex(1)
    heading = 1 if order == "list-then-heading" else 0
    actual_list = "none" if heading else list_state
    expected = (
        expected_block("First", heading, actual_list, False, (True, False, False)),
        expected_block("Second", heading, actual_list, False, (True, False, False)),
    )
    assert tuple(inspect_block(window, index) for index in range(2)) == expected
    if order == "heading-then-list":
        assert inspect_toolbar(window) == expected_toolbar(
            0, list_state, False, (True, False, False)
        )
    save_and_reopen(window, tmp_path / "consecutive.md", monkeypatch)
    assert tuple(inspect_block(window, index) for index in range(2)) == expected


def test_adjacent_supported_blocks_keep_meaning_after_save_and_reopen(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lines = (
        "Heading one",
        "Heading two",
        "Bullet one",
        "Bullet two",
        "Number one",
        "Number two",
        "Quote one",
        "Quote two",
        "Bold text",
        "Italic text",
        "Struck text",
    )
    window.editor.setPlainText("\n".join(lines))
    document = window.editor.document()

    def select_block(index: int) -> None:
        window.editor.setTextCursor(QTextCursor(document.findBlockByNumber(index)))

    for index, level in ((0, 1), (1, 2)):
        select_block(index)
        window.style_selector.setCurrentIndex(level)
    for index, action_names in (
        (2, ("bullet_action",)),
        (3, ("bullet_action",)),
        (4, ("numbered_action",)),
        (5, ("numbered_action",)),
        (6, ("bullet_action", "quote_action")),
        (7, ("bullet_action", "quote_action")),
    ):
        select_block(index)
        for name in action_names:
            getattr(window, name).trigger()
    for index, action_name in ((8, "bold_action"), (9, "italic_action"), (10, "strike_action")):
        block = document.findBlockByNumber(index)
        cursor = QTextCursor(block)
        cursor.setPosition(block.position() + len(block.text()), QTextCursor.MoveMode.KeepAnchor)
        window.editor.setTextCursor(cursor)
        getattr(window, action_name).trigger()

    expected = tuple(
        expected_block(text, heading, list_state, quote, inline)
        for text, heading, list_state, quote, inline in (
            (lines[0], 1, "none", False, (True, False, False)),
            (lines[1], 2, "none", False, (True, False, False)),
            (lines[2], 0, "bullet", False, (False, False, False)),
            (lines[3], 0, "bullet", False, (False, False, False)),
            (lines[4], 0, "numbered", False, (False, False, False)),
            (lines[5], 0, "numbered", False, (False, False, False)),
            (lines[6], 0, "none", True, (False, False, False)),
            (lines[7], 0, "none", True, (False, False, False)),
            (lines[8], 0, "none", False, (True, False, False)),
            (lines[9], 0, "none", False, (False, True, False)),
            (lines[10], 0, "none", False, (False, False, True)),
        )
    )
    assert tuple(inspect_block(window, index) for index in range(len(lines))) == expected
    save_and_reopen(window, tmp_path / "adjacent.md", monkeypatch)
    assert tuple(inspect_block(window, index) for index in range(len(lines))) == expected


@pytest.mark.parametrize(
    ("list_state", "inline"),
    [
        ("bullet", (True, False, False)),
        ("bullet", (False, False, True)),
        ("none", (False, False, True)),
    ],
    ids=("bullet-bold", "bullet-strike", "paragraph-strike"),
)
def test_owner_inline_round_trip_regressions(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    list_state: str,
    inline: tuple[bool, bool, bool],
) -> None:
    create_typing_state(window, 0, list_state, False, inline)
    type_text(window)
    after_save, reopened = save_and_reopen(window, tmp_path / "regression.md", monkeypatch)
    expected = expected_block(TEXT, 0, list_state, False, inline)
    assert after_save == expected
    assert reopened == expected


@pytest.mark.parametrize(
    ("list_state", "action_name", "inline"),
    [
        ("bullet", "bold_action", (True, False, False)),
        ("bullet", "strike_action", (False, False, True)),
        ("none", "strike_action", (False, False, True)),
    ],
    ids=("selected-bullet-bold", "selected-bullet-strike", "selected-paragraph-strike"),
)
def test_owner_selected_text_round_trip_regressions(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    list_state: str,
    action_name: str,
    inline: tuple[bool, bool, bool],
) -> None:
    create_typing_state(window, 0, list_state, False)
    type_text(window)
    select_text(window)
    getattr(window, action_name).trigger()
    assert_live_state(window, TEXT, 0, list_state, False, inline)
    after_save, reopened = save_and_reopen(window, tmp_path / "selected.md", monkeypatch)
    expected = expected_block(TEXT, 0, list_state, False, inline)
    assert after_save == expected
    assert reopened == expected


def test_quote_reopens_as_quote_instead_of_code(
    window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    create_typing_state(window, 0, "none", True)
    type_text(window)
    _, reopened = save_and_reopen(window, tmp_path / "quote.md", monkeypatch)
    assert reopened == expected_block(TEXT, 0, "none", True, (False, False, False))
    block = window.editor.document().firstBlock()
    assert block.blockFormat().indent() == 0
    assert not block.begin().fragment().charFormat().fontFamilies()


@pytest.mark.parametrize("inline", PARAGRAPH_INLINE)
@pytest.mark.parametrize("action_index", (0, 1, 2), ids=("Bold", "Italic", "Strike"))
def test_inline_action_toggles_each_typing_state(
    window: MainWindow, inline: tuple[bool, bool, bool], action_index: int
) -> None:
    create_typing_state(window, 0, "none", False, inline)
    type_text(window)
    select_text(window)
    actions = (window.bold_action, window.italic_action, window.strike_action)
    actions[action_index].trigger()
    expected_inline = list(inline)
    expected_inline[action_index] = not expected_inline[action_index]
    if expected_inline[action_index] and action_index == 2:
        expected_inline[0:2] = [False, False]
    elif expected_inline[action_index] and inline[2]:
        expected_inline[2] = False
    assert_live_state(
        window, TEXT, 0, "none", False, (expected_inline[0], expected_inline[1], expected_inline[2])
    )


@pytest.mark.parametrize("source", HEADING_LEVELS)
@pytest.mark.parametrize("target", HEADING_LEVELS)
@pytest.mark.parametrize("list_state", LIST_STATES)
@pytest.mark.parametrize("quote", (False, True))
def test_heading_choice_creates_only_standalone_headings(
    window: MainWindow, source: int, target: int, list_state: str, quote: bool
) -> None:
    inline = (True, False, False)
    create_typing_state(window, source, list_state, quote, inline)
    type_text(window)
    window.style_selector.setCurrentIndex(target)
    if target and not quote:
        assert_live_state(window, TEXT, target, "none", False, inline)
    else:
        assert_live_state(window, TEXT, 0, "none" if quote else list_state, quote, inline)


@pytest.mark.parametrize("source", LIST_STATES)
@pytest.mark.parametrize("target", ("bullet", "numbered"))
@pytest.mark.parametrize("quote", (False, True))
def test_list_action_exits_quote_and_preserves_inline(
    window: MainWindow, source: str, target: str, quote: bool
) -> None:
    inline = (True, False, False)
    create_typing_state(window, 0, source, quote, inline)
    type_text(window)
    (window.bullet_action if target == "bullet" else window.numbered_action).trigger()
    expected_list = "none" if source == target and not quote else target
    assert_live_state(window, TEXT, 0, expected_list, False, inline)


@pytest.mark.parametrize("heading", (1, 2, 3))
@pytest.mark.parametrize("action_name", ("bullet_action", "numbered_action"))
def test_list_action_normalizes_heading_to_paragraph(
    window: MainWindow, heading: int, action_name: str
) -> None:
    create_typing_state(window, heading, "none", False, (True, False, False))
    type_text(window)
    getattr(window, action_name).trigger()
    list_state = "bullet" if action_name == "bullet_action" else "numbered"
    assert_live_state(window, TEXT, 0, list_state, False, (True, False, False))


@pytest.mark.parametrize("list_state", LIST_STATES)
@pytest.mark.parametrize("quote", (False, True))
def test_quote_action_exits_list_and_preserves_inline(
    window: MainWindow, list_state: str, quote: bool
) -> None:
    inline = (True, False, False)
    create_typing_state(window, 2, list_state, quote, inline)
    type_text(window)
    window.quote_action.trigger()
    assert_live_state(window, TEXT, 0, "none", not quote, inline)


@pytest.mark.parametrize("heading", HEADING_LEVELS)
@pytest.mark.parametrize("list_state", LIST_STATES)
@pytest.mark.parametrize("quote", (False, True))
def test_enter_after_text_uses_heading_and_structure_contract(
    window: MainWindow, heading: int, list_state: str, quote: bool
) -> None:
    create_typing_state(window, heading, list_state, quote)
    type_text(window)
    initial = inspect_block(window)
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    initial_heading = 0 if quote or list_state != "none" else heading
    initial_list = "none" if quote else list_state
    initial_inline = (heading != 0, False, False)
    next_heading = 0
    previous = inspect_block(window)
    count = window.editor.document().blockCount()
    expected_new_block = expected_block("", next_heading, initial_list, quote, initial_inline)
    actual_new_block = inspect_block(window, 1)[:4]
    actual_controls = inspect_toolbar(window)
    expected_controls = expected_toolbar(next_heading, initial_list, quote, initial_inline)
    type_text(window, "Next writing")
    expected_previous = expected_block(TEXT, initial_heading, initial_list, quote, initial_inline)
    expected_typed = expected_block(
        "Next writing", next_heading, initial_list, quote, initial_inline
    )
    actual_typed = inspect_block(window, 1)
    assert (
        initial,
        previous,
        count,
        actual_new_block,
        actual_controls,
        actual_typed,
    ) == (
        expected_previous,
        expected_previous,
        2,
        expected_new_block[:4],
        expected_controls,
        expected_typed,
    ), (
        f"before Enter: {initial!r}; after Enter previous: {previous!r}; "
        f"new: {actual_new_block!r}; toolbar: {actual_controls!r}; "
        f"after typing: {actual_typed!r}; expected previous: {expected_previous!r}, "
        f"new: {expected_new_block[:4]!r}, toolbar: {expected_controls!r}, "
        f"typed: {expected_typed!r}"
    )


@pytest.mark.parametrize(
    ("heading", "list_state", "quote"),
    [
        (heading, list_state, quote)
        for heading in HEADING_LEVELS
        for list_state in LIST_STATES
        for quote in (False, True)
        if list_state != "none" or quote
    ],
)
def test_enter_on_blank_structured_block_exits_to_paragraph(
    window: MainWindow, heading: int, list_state: str, quote: bool
) -> None:
    create_typing_state(window, heading, list_state, quote)
    before = inspect_block(window)[:4]
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    actual = (
        window.editor.document().blockCount(),
        inspect_block(window)[:4],
        inspect_toolbar(window),
    )
    expected = (
        1,
        ("", 0, None, False),
        expected_toolbar(0, "none", False, (heading != 0, False, False)),
    )
    type_text(window)
    after_typing = inspect_block(window)
    assert (before, actual, after_typing) == (
        (
            "",
            0,
            expected_block("", 0, "none" if quote else list_state, quote, (False, False, False))[2],
            quote,
        ),
        expected,
        expected_block(TEXT, 0, "none", False, (heading != 0, False, False)),
    ), f"before blank Enter: {before!r}; after: {actual!r}; after typing: {after_typing!r}"


@pytest.mark.parametrize(("heading", "list_state", "quote", "inline"), SAFE_STATES)
def test_inline_typing_modes_survive_enter(
    window: MainWindow, inline: tuple[bool, bool, bool], heading: int, list_state: str, quote: bool
) -> None:
    create_typing_state(window, heading, list_state, quote, inline)
    type_text(window)
    initial = inspect_block(window)
    QTest.keyClick(window.editor, Qt.Key.Key_Return)
    expected_heading = 0 if list_state == "none" and not quote else heading
    toolbar_after_enter = inspect_toolbar(window)
    type_text(window, "Next writing")
    typed = inspect_block(window, 1)
    toolbar_after_typing = inspect_toolbar(window)
    expected_controls = expected_toolbar(expected_heading, list_state, quote, inline)
    expected_typed = expected_block("Next writing", expected_heading, list_state, quote, inline)
    expected_initial = expected_block(TEXT, heading, list_state, quote, inline)
    assert (initial, toolbar_after_enter, typed, toolbar_after_typing) == (
        expected_initial,
        expected_controls,
        expected_typed,
        expected_controls,
    ), (
        f"before Enter: {initial!r}; toolbar after Enter: {toolbar_after_enter!r}; "
        f"typed new block: {typed!r}; toolbar after typing: {toolbar_after_typing!r}; "
        f"expected initial: {expected_initial!r}, toolbar: {expected_controls!r}, "
        f"typed: {expected_typed!r}"
    )
