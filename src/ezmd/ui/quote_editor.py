"""The native writing surface with a presentation-only quote rail."""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QTextCursor, QTextFormat
from PySide6.QtWidgets import QTextEdit


class QuoteTextEdit(QTextEdit):
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
                x = rect.left() - self._rail_gap - self._rail_width
                height = round(layout.blockBoundingRect(block).height())
                painter.drawLine(x, rect.top(), x, rect.top() + height - 1)
            block = block.next()
        if painter is not None:
            painter.end()
