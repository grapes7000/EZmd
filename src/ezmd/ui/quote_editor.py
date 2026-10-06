"""The native writing surface with a presentation-only quote rail."""

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import QTextEdit


class QuoteTextEdit(QTextEdit):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Apply the agreed new-block rules after Qt performs its native Enter edit."""
        if (
            event.key() not in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            or event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier
            or self.textCursor().hasSelection()
        ):
            super().keyPressEvent(event)
            return

        block = self.textCursor().block()
        heading = block.blockFormat().headingLevel()
        structured = bool(block.textList()) or (
            block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1
        )
        blank = not block.text().strip()
        before = self.currentCharFormat()
        super().keyPressEvent(event)

        new_block = self.textCursor().block()
        new_cursor = QTextCursor(new_block)
        block_format = new_block.blockFormat()
        if structured and blank:
            text_list = new_block.textList()
            if text_list:
                text_list.remove(new_block)
            block_format.clearProperty(QTextFormat.Property.BlockQuoteLevel)
            block_format.setIndent(0)
            block_format.setHeadingLevel(0)
            new_cursor.setBlockFormat(block_format)
        elif structured and heading:
            # An imported heading-list item must not create another unsupported heading-list item.
            block_format.setHeadingLevel(0)
            new_cursor.setBlockFormat(block_format)
        elif heading:
            block_format.setHeadingLevel(0)
            new_cursor.setBlockFormat(block_format)

        # Qt resets heading typography on Return. Inline buttons represent typing modes,
        # so restore those modes on the new block without converting Markdown.
        typing_format = QTextCharFormat()
        typing_format.setFontWeight(
            QFont.Weight.Bold if before.fontWeight() >= QFont.Weight.Bold else QFont.Weight.Normal
        )
        typing_format.setFontItalic(before.fontItalic())
        typing_format.setFontStrikeOut(before.fontStrikeOut())
        self.mergeCurrentCharFormat(typing_format)

    def set_quote_rail(self, color: str, width: int, gap: int) -> None:
        self._rail_color = QColor(color)
        self._rail_width = width
        self._rail_gap = gap
        self.viewport().update()

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        viewport = self.viewport()
        block = self.cursorForPosition(QPoint(0, event.rect().top())).block()
        layout = self.document().documentLayout()
        painter: QPainter | None = None
        while block.isValid():
            rect = self.cursorRect(QTextCursor(block))
            if rect.top() > event.rect().bottom():
                break
            if block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1:
                if painter is None:
                    painter = QPainter(viewport)
                    painter.setClipRect(event.rect())
                    painter.setPen(QPen(self._rail_color, self._rail_width))
                # Unindented quotes need the rail inside the viewport, not clipped off its edge.
                x = max(self._rail_width, rect.left() - self._rail_gap - self._rail_width)
                height = round(layout.blockBoundingRect(block).height())
                painter.drawLine(x, rect.top(), x, rect.top() + height - 1)
            block = block.next()
        if painter is not None:
            painter.end()
