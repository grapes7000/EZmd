"""Preserve editor whitespace that Qt's native Markdown conversion otherwise drops."""

from PySide6.QtGui import QTextBlock, QTextCursor, QTextDocument

# Qt Markdown ignores the comment but keeps the invisible separator as ordinary text.
# Only files carrying our header are decoded; external Markdown remains best-effort.
HEADER = "<!-- EZmd whitespace v1 -->\n\n"
MARKER = "\u2063"  # Invisible separator: one marks an empty block; two encode a literal one.
NONBREAKING_SPACE = "\u00a0"


def _blocks_backward(document: QTextDocument) -> list[QTextBlock]:
    blocks: list[QTextBlock] = []
    block = document.lastBlock()
    while block.isValid():
        blocks.append(block)
        block = block.previous()
    return blocks


def _replace_character(document: QTextDocument, position: int, replacement: str) -> None:
    cursor = QTextCursor(document)
    cursor.setPosition(position)
    cursor.setPosition(position + 1, QTextCursor.MoveMode.KeepAnchor)
    # Retain the original inline flags when a space or literal marker is encoded.
    char_format = cursor.charFormat()
    cursor.insertText(replacement, char_format)


def _utf16_length(text: str) -> int:
    # QTextCursor positions count UTF-16 code units; Python string indexes do not.
    return len(text.encode("utf-16-le")) // 2


def serialize(document: QTextDocument) -> str:
    """Use native Markdown, encoding only whitespace Qt would otherwise discard."""
    block = document.begin()
    needs_encoding = False
    while block.isValid():
        text = block.text()
        if not text or text.startswith(" ") or MARKER in text:
            needs_encoding = True
            break
        block = block.next()
    if not needs_encoding:
        return document.toMarkdown()

    copy = document.clone()
    for block in _blocks_backward(copy):
        original = block.text()
        for offset in range(len(original) - 1, -1, -1):
            if original[offset] == MARKER:
                position = block.position() + _utf16_length(original[:offset])
                _replace_character(copy, position, MARKER * 2)
        leading_spaces = len(original) - len(original.lstrip(" "))
        for offset in range(leading_spaces - 1, -1, -1):
            _replace_character(copy, block.position() + offset, NONBREAKING_SPACE)
        if not original or leading_spaces:
            QTextCursor(block).insertText(MARKER)
        if not original:
            source_list = document.findBlockByNumber(block.blockNumber()).textList()
            if source_list:
                # QTextDocument.clone() drops native list membership on empty list items.
                QTextCursor(block).createList(source_list.format())
    return HEADER + copy.toMarkdown()


def restore(document: QTextDocument, markdown: str) -> None:
    """Decode only our own whitespace markers in a temporary parsed document."""
    if not markdown.startswith(HEADER):
        return
    for block in _blocks_backward(document):
        text = block.text()
        if text == MARKER:
            _replace_character(document, block.position(), "")
            continue
        if text.startswith(MARKER + NONBREAKING_SPACE):
            # The first marker tags converted leading spaces, not a literal marker.
            _replace_character(document, block.position(), "")
            text = block.text()
            leading = len(text) - len(text.lstrip(NONBREAKING_SPACE))
            for offset in range(leading - 1, -1, -1):
                _replace_character(document, block.position() + offset, " ")
            text = block.text()
        offset = len(text) - 1
        while offset > 0:
            if text[offset - 1 : offset + 1] == MARKER * 2:
                _replace_character(document, block.position() + _utf16_length(text[:offset]), "")
                offset -= 2  # Each escaped pair represents one literal separator.
            else:
                offset -= 1
