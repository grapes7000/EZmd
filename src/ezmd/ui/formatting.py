"""Formatting operations on the one native Qt document."""

from collections.abc import Iterator

from PySide6.QtGui import (
    QFont,
    QTextBlock,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
    QTextListFormat,
)
from PySide6.QtWidgets import QTextEdit

QUOTE_LEVEL = QTextFormat.Property.BlockQuoteLevel


def affected_blocks(cursor: QTextCursor) -> Iterator[QTextBlock]:
    document = cursor.document()
    start = cursor.selectionStart() if cursor.hasSelection() else cursor.position()
    end = cursor.selectionEnd() - 1 if cursor.hasSelection() else start
    block = document.findBlock(start)
    last = document.findBlock(max(start, end))
    while block.isValid():
        yield block
        if block == last:
            break
        block = block.next()


def character_states(editor: QTextEdit) -> tuple[bool, bool, bool]:
    cursor = editor.textCursor()
    if not cursor.hasSelection():
        fmt = editor.currentCharFormat()
        return (fmt.fontWeight() >= QFont.Weight.Bold, fmt.fontItalic(), fmt.fontStrikeOut())
    start, end = cursor.selectionStart(), cursor.selectionEnd()
    found_text = False
    bold, italic, struck = True, True, True
    for block in affected_blocks(cursor):
        fragments = block.begin()
        while not fragments.atEnd():
            fragment = fragments.fragment()
            if fragment.position() < end and fragment.position() + fragment.length() > start:
                found_text = True
                fmt = fragment.charFormat()
                bold &= fmt.fontWeight() >= QFont.Weight.Bold
                italic &= fmt.fontItalic()
                struck &= fmt.fontStrikeOut()
            fragments += 1
    return (found_text and bold, found_text and italic, found_text and struck)


def toggle_character(editor: QTextEdit, kind: str) -> None:
    cursor = editor.textCursor()
    enabled = not character_states(editor)[("bold", "italic", "strike").index(kind)]
    if (
        enabled
        and kind in ("strike", "italic")
        and any(block.blockFormat().headingLevel() for block in affected_blocks(cursor))
    ):
        return
    if (
        kind == "bold"
        and not enabled
        and any(block.blockFormat().headingLevel() for block in affected_blocks(cursor))
    ):
        return
    fmt = QTextCharFormat()
    if kind == "bold":
        fmt.setFontWeight(QFont.Weight.Bold if enabled else QFont.Weight.Normal)
    elif kind == "italic":
        fmt.setFontItalic(enabled)
    else:
        fmt.setFontStrikeOut(enabled)
    # Qt's Markdown writer crosses emphasis delimiters when strike overlaps emphasis.
    if enabled and kind in ("bold", "italic"):
        fmt.setFontStrikeOut(False)
    elif enabled:
        fmt.setFontWeight(QFont.Weight.Normal)
        fmt.setFontItalic(False)
    if cursor.hasSelection():
        cursor.beginEditBlock()
        cursor.mergeCharFormat(fmt)
        cursor.endEditBlock()
    else:
        editor.mergeCurrentCharFormat(fmt)


def block_style(cursor: QTextCursor) -> int | None:
    styles = {block.blockFormat().headingLevel() for block in affected_blocks(cursor)}
    return styles.pop() if len(styles) == 1 else None


def apply_block_style(editor: QTextEdit, level: int, point_size: float) -> None:
    cursor = editor.textCursor()
    char_fmt = QTextCharFormat()
    char_fmt.setFontPointSize(point_size)
    if level:
        char_fmt.setFontWeight(QFont.Weight.Bold)
        char_fmt.setFontItalic(False)
        char_fmt.setFontStrikeOut(False)
    cursor.beginEditBlock()
    for block in affected_blocks(cursor):
        block_cursor = QTextCursor(block)
        was_list_item = bool(block.textList())
        if level and was_list_item:
            # A heading is a standalone block; remove both structures from a quoted list.
            block.textList().remove(block)
        fmt = block.blockFormat()
        if level and was_list_item and fmt.hasProperty(QUOTE_LEVEL):
            fmt.clearProperty(QUOTE_LEVEL)
            fmt.setIndent(0)
        # Qt Markdown cannot import a quoted heading; retain Quote as Paragraph.
        fmt.setHeadingLevel(0 if level and fmt.property(QUOTE_LEVEL) == 1 else level)
        block_cursor.setBlockFormat(fmt)
        # Qt draws list markers with the block character format, not text fragments.
        block_cursor.mergeBlockCharFormat(char_fmt)
        block_cursor.setPosition(
            block.position() + block.length() - 1, QTextCursor.MoveMode.KeepAnchor
        )
        block_cursor.mergeCharFormat(char_fmt)
    cursor.endEditBlock()
    if not cursor.hasSelection():
        editor.mergeCurrentCharFormat(char_fmt)


def list_style(cursor: QTextCursor) -> QTextListFormat.Style | None:
    styles = {
        block.textList().format().style() if block.textList() else None
        for block in affected_blocks(cursor)
    }
    return styles.pop() if len(styles) == 1 else None


def toggle_list(editor: QTextEdit, style: QTextListFormat.Style) -> None:
    cursor = editor.textCursor()
    blocks = list(affected_blocks(cursor))
    removing = list_style(cursor) == style
    cursor.beginEditBlock()
    if removing:
        for block in blocks:
            text_list = block.textList()
            if text_list:
                text_list.remove(block)
            fmt = block.blockFormat()
            fmt.setIndent(0)
            QTextCursor(block).setBlockFormat(fmt)
    else:
        for block in blocks:
            fmt = block.blockFormat()
            if fmt.indent() or fmt.hasProperty(QUOTE_LEVEL):
                fmt.setIndent(0)
                fmt.clearProperty(QUOTE_LEVEL)
                QTextCursor(block).setBlockFormat(fmt)
        list_cursor = QTextCursor(blocks[0])
        if len(blocks) > 1:
            last = blocks[-1]
            list_cursor.setPosition(
                last.position() + last.length() - 1, QTextCursor.MoveMode.KeepAnchor
            )
        list_format = QTextListFormat()
        list_format.setStyle(style)
        list_format.setIndent(1)
        list_cursor.createList(list_format)
    cursor.endEditBlock()


def quote_active(cursor: QTextCursor) -> bool:
    return all(block.blockFormat().property(QUOTE_LEVEL) == 1 for block in affected_blocks(cursor))


def toggle_quote(editor: QTextEdit, paragraph_point_size: float) -> None:
    cursor = editor.textCursor()
    removing = quote_active(cursor)
    cursor.beginEditBlock()
    for block in affected_blocks(cursor):
        if not removing and block.textList():
            block.textList().remove(block)
        block_cursor = QTextCursor(block)
        fmt = block.blockFormat()
        if removing:
            fmt.clearProperty(QUOTE_LEVEL)
        else:
            fmt.setProperty(QUOTE_LEVEL, 1)
        # Block indentation serializes as code inside a quote; the painted rail provides its cue.
        fmt.setIndent(0)
        block_cursor.setBlockFormat(fmt)
    cursor.endEditBlock()
    if not removing and any(
        block.blockFormat().headingLevel() for block in affected_blocks(cursor)
    ):
        apply_block_style(editor, 0, paragraph_point_size)
