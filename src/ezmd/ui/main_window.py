"""The one-document native writing window."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QCloseEvent,
    QKeySequence,
    QTextListFormat,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ezmd.core.files import read_text, write_text
from ezmd.ui import formatting
from ezmd.ui.quote_editor import QuoteTextEdit
from ezmd.ui.visual_profiles import (
    DEFAULT_PROFILE,
    PROFILES,
    apply_profile,
    heading_point_size,
    system_colors,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_path: Path | None = None
        self.editor = QuoteTextEdit(self)
        self.editor.setAcceptRichText(False)
        self.editor.setAutoFormatting(QuoteTextEdit.AutoFormattingFlag.AutoNone)

        central = QWidget(self)
        self.content_layout = QVBoxLayout(central)
        self.content_layout.addWidget(self.editor)
        self.setCentralWidget(central)

        self.toolbar = QToolBar("Writing", self)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(self.toolbar)

        file_menu = self.menuBar().addMenu("&File")
        edit_menu = self.menuBar().addMenu("&Edit")
        view_menu = self.menuBar().addMenu("&View")
        self.new_action = self._add_action("New", QKeySequence.StandardKey.New, self.new_document)
        self.open_action = self._add_action(
            "Open", QKeySequence.StandardKey.Open, self.open_document
        )
        self.save_action = self._add_action(
            "Save", QKeySequence.StandardKey.Save, self.save_document
        )
        self.undo_action = self._add_action("Undo", QKeySequence.StandardKey.Undo, self.editor.undo)
        self.redo_action = self._add_action("Redo", QKeySequence.StandardKey.Redo, self.editor.redo)
        for action in (self.new_action, self.open_action, self.save_action):
            file_menu.addAction(action)
        for action in (self.undo_action, self.redo_action):
            edit_menu.addAction(action)

        profile_menu = view_menu.addMenu("Visual Profile")
        profile_group = QActionGroup(self)
        self.profile_actions: dict[str, QAction] = {}
        for name in PROFILES:
            action = QAction(name, self)
            action.setCheckable(True)
            profile_group.addAction(action)
            profile_menu.addAction(action)
            action.triggered.connect(
                lambda _checked=False, profile=name: self._change_profile(profile)
            )
            self.profile_actions[name] = action
        self.profile_actions[DEFAULT_PROFILE].setChecked(True)

        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        document = self.editor.document()
        document.undoAvailable.connect(self.undo_action.setEnabled)
        document.redoAvailable.connect(self.redo_action.setEnabled)
        document.modificationChanged.connect(self._update_title)

        for action, glyph in ((self.undo_action, "↶"), (self.redo_action, "↷")):
            action.setIconText(glyph)
            self.toolbar.addAction(action)
            button = self.toolbar.widgetForAction(action)
            if isinstance(button, QToolButton):
                button.setObjectName("historyButton")
                button.setAccessibleName(action.text())
                button.setToolTip(action.text())
                button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toolbar.addSeparator()
        self.style_selector = QComboBox(self.toolbar)
        self.style_selector.addItems(["Paragraph", "H1", "H2", "H3"])
        self.style_selector.setPlaceholderText("Mixed")
        self.style_selector.setAccessibleName("Paragraph style")
        self.toolbar.addWidget(self.style_selector)
        self.style_selector.currentIndexChanged.connect(self._apply_style)
        self.toolbar.addSeparator()
        self.bold_action = self._format_action("B", "Bold", QKeySequence.StandardKey.Bold)
        self.italic_action = self._format_action("I", "Italic", QKeySequence.StandardKey.Italic)
        self.strike_action = self._format_action("S", "Strikethrough")
        strike_button = self.toolbar.widgetForAction(self.strike_action)
        if isinstance(strike_button, QToolButton):
            font = strike_button.font()
            font.setStrikeOut(True)
            strike_button.setFont(font)
        self.toolbar.addSeparator()
        self.bullet_action = self._format_action("•", "Bulleted list")
        self.numbered_action = self._format_action("1.", "Numbered list")
        self.quote_action = self._format_action("Quote", "Blockquote")
        for action, kind in (
            (self.bold_action, "bold"),
            (self.italic_action, "italic"),
            (self.strike_action, "strike"),
        ):
            action.triggered.connect(lambda _checked=False, kind=kind: self._toggle_character(kind))
        self.bullet_action.triggered.connect(
            lambda: self._toggle_list(QTextListFormat.Style.ListDisc)
        )
        self.numbered_action.triggered.connect(
            lambda: self._toggle_list(QTextListFormat.Style.ListDecimal)
        )
        self.quote_action.triggered.connect(self._toggle_quote)

        self.editor.cursorPositionChanged.connect(self._sync_formatting)
        self.editor.selectionChanged.connect(self._sync_formatting)
        self.editor.currentCharFormatChanged.connect(self._sync_formatting)
        self.editor.textChanged.connect(self._sync_formatting)
        self.colors = system_colors(self.palette())
        self._change_profile(DEFAULT_PROFILE)
        self._sync_formatting()
        self._update_title()
        self.editor.setFocus()

    def _add_action(
        self, label: str, shortcut: QKeySequence.StandardKey, callback: Callable[[], object]
    ) -> QAction:
        action = QAction(label, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        return action

    def _format_action(
        self, label: str, tooltip: str, shortcut: QKeySequence.StandardKey | None = None
    ) -> QAction:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setToolTip(tooltip)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        self.toolbar.addAction(action)
        button = self.toolbar.widgetForAction(action)
        if isinstance(button, QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            button.setAccessibleName(tooltip)
        return action

    def _apply_style(self, level: int) -> None:
        if level < 0:
            return
        formatting.apply_block_style(self.editor, level, heading_point_size(self.editor, level))
        self._after_formatting()

    def _toggle_character(self, kind: str) -> None:
        formatting.toggle_character(self.editor, kind)
        self._after_formatting()

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        formatting.toggle_list(self.editor, style)
        self._after_formatting()

    def _toggle_quote(self) -> None:
        formatting.toggle_quote(self.editor)
        self._after_formatting()

    def _after_formatting(self) -> None:
        self.editor.setFocus()

    def _sync_formatting(self) -> None:
        cursor = self.editor.textCursor()
        style = formatting.block_style(cursor)
        with QSignalBlocker(self.style_selector):
            self.style_selector.setCurrentIndex(-1 if style is None else style)
        bold, italic, struck = formatting.character_states(self.editor)
        self.bold_action.setChecked(bold)
        self.italic_action.setChecked(italic)
        self.strike_action.setChecked(struck)
        list_style = formatting.list_style(cursor)
        self.bullet_action.setChecked(list_style == QTextListFormat.Style.ListDisc)
        self.numbered_action.setChecked(list_style == QTextListFormat.Style.ListDecimal)
        self.quote_action.setChecked(formatting.quote_active(cursor))

    def _update_title(self) -> None:
        name = self.current_path.name if self.current_path is not None else "Untitled"
        modified = self.editor.document().isModified()
        self.setWindowTitle(f"{name}{' *' if modified else ''} — EZmd")

    def _change_profile(self, name: str) -> None:
        apply_profile(
            self.toolbar,
            self.editor,
            self.content_layout,
            self.style_selector,
            name,
            self.colors,
        )

    def _confirm_unsaved_changes(self) -> bool:
        if not self.editor.document().isModified():
            return True
        choice = QMessageBox.warning(
            self,
            "Unsaved changes",
            "Save changes to this document?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if choice == QMessageBox.StandardButton.Save:
            return self.save_document()
        return choice == QMessageBox.StandardButton.Discard

    def new_document(self) -> None:
        if not self._confirm_unsaved_changes():
            return
        self.editor.setPlainText("")
        self.current_path = None
        self.editor.document().setModified(False)
        self._update_title()
        self.editor.setFocus()

    def open_document(self) -> None:
        if not self._confirm_unsaved_changes():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "Markdown and Text (*.md *.markdown *.txt);;All Files (*)",
        )
        if not filename:
            return
        path = Path(filename)
        try:
            text = read_text(path)
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(
                self, "Could not open document", f"Could not open {path.name}: {error}"
            )
            return
        self.editor.setPlainText(text)
        self.current_path = path
        self.editor.document().setModified(False)
        self._update_title()
        self.editor.setFocus()

    def save_document(self) -> bool:
        path = self.current_path
        if path is None:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Document",
                "",
                "Markdown (*.md *.markdown);;Text (*.txt);;All Files (*)",
            )
            if not filename:
                return False
            path = Path(filename)
        try:
            write_text(path, self.editor.toPlainText())
        except (OSError, UnicodeError) as error:
            QMessageBox.critical(
                self, "Could not save document", f"Could not save {path.name}: {error}"
            )
            return False
        self.current_path = path
        self.editor.document().setModified(False)
        self._update_title()
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._confirm_unsaved_changes():
            event.accept()
        else:
            event.ignore()
