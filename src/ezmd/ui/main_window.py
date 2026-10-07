"""The one-document native writing window."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QCloseEvent,
    QFont,
    QKeySequence,
    QTextDocument,
    QTextFormat,
    QTextListFormat,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ezmd.core.files import read_text, write_text
from ezmd.ui import formatting, markdown_whitespace
from ezmd.ui.quote_editor import QuoteTextEdit
from ezmd.ui.visual_profiles import (
    DEFAULT_PROFILE,
    DEFAULT_THEME,
    PROFILES,
    SPACE_6,
    SPACE_8,
    THEMES,
    apply_profile,
    apply_sidebar_style,
    heading_point_size,
    theme_palette,
)

SIDEBAR_WIDTH = 240
SIDEBAR_MIN_WIDTH = 160
SIDEBAR_MAX_WIDTH = 360
SIDEBAR_RAIL_WIDTH = 40


def document_semantics(document: QTextDocument) -> tuple[tuple[object, ...], ...]:
    """Compare supported meaning, combining adjacent fragments with the same inline flags."""
    blocks: list[tuple[object, ...]] = []
    block = document.begin()
    while block.isValid():
        text_list = block.textList()
        list_style = text_list.format().style() if text_list else None
        runs: list[tuple[str, bool, bool, bool]] = []
        iterator = block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            text = fragment.text()
            if text:
                fmt = fragment.charFormat()
                flags = (
                    fmt.fontWeight() >= QFont.Weight.Bold,
                    fmt.fontItalic(),
                    fmt.fontStrikeOut(),
                )
                if runs and runs[-1][1:] == flags:
                    previous = runs[-1]
                    runs[-1] = (previous[0] + text, *flags)
                else:
                    runs.append((text, *flags))
            iterator += 1
        blocks.append(
            (
                block.text(),
                block.blockFormat().headingLevel(),
                list_style,
                block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1,
                tuple(runs),
            )
        )
        block = block.next()
    return tuple(blocks)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_path: Path | None = None
        self.editor_pane = QWidget(self)
        self.editor = QuoteTextEdit(self.editor_pane)
        self.editor.setAcceptRichText(False)
        self.editor.setAutoFormatting(QuoteTextEdit.AutoFormattingFlag.AutoNone)

        pane_layout = QVBoxLayout(self.editor_pane)
        pane_layout.setContentsMargins(0, 0, 0, 0)
        pane_layout.setSpacing(0)
        self.toolbar = QToolBar("Writing", self.editor_pane)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        pane_layout.addWidget(self.toolbar)
        # Keep profile margins around only the editor, not the full-width toolbar.
        self.content_layout = QVBoxLayout()
        self.content_layout.addWidget(self.editor)
        pane_layout.addLayout(self.content_layout, 1)
        self.sidebar = QWidget(self)
        self.sidebar.setObjectName("documentsSidebar")
        self.sidebar.setAccessibleName("Documents sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(SPACE_8, SPACE_8, SPACE_8, SPACE_8)
        sidebar_layout.setSpacing(SPACE_8)
        self.sidebar_header = QWidget(self.sidebar)
        header_layout = QHBoxLayout(self.sidebar_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_title = QLabel("Documents", self.sidebar_header)
        self.sidebar_title.setObjectName("sidebarTitle")
        header_layout.addWidget(self.sidebar_title)
        header_layout.addStretch()
        self.sidebar_collapse_button = QToolButton(self.sidebar_header)
        self.sidebar_collapse_button.setObjectName("sidebarButton")
        self.sidebar_collapse_button.setText("<")
        self.sidebar_collapse_button.setAccessibleName("Collapse sidebar")
        self.sidebar_collapse_button.setToolTip("Collapse sidebar")
        self.sidebar_collapse_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.sidebar_collapse_button.clicked.connect(self._collapse_sidebar)
        header_layout.addWidget(self.sidebar_collapse_button)
        sidebar_layout.addWidget(self.sidebar_header)
        self.sidebar_expand_button = QToolButton(self.sidebar)
        self.sidebar_expand_button.setObjectName("sidebarButton")
        self.sidebar_expand_button.setText(">")
        self.sidebar_expand_button.setAccessibleName("Expand sidebar")
        self.sidebar_expand_button.setToolTip("Expand sidebar")
        self.sidebar_expand_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.sidebar_expand_button.clicked.connect(self._expand_sidebar)
        sidebar_layout.addWidget(self.sidebar_expand_button, 0, Qt.AlignmentFlag.AlignHCenter)
        self.sidebar_expand_button.hide()
        sidebar_layout.addStretch()
        self.sidebar.setMinimumWidth(SIDEBAR_MIN_WIDTH)
        self.sidebar.setMaximumWidth(SIDEBAR_MAX_WIDTH)
        self._expanded_sidebar_width = SIDEBAR_WIDTH
        self._sidebar_collapsed = False

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(SPACE_6)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.editor_pane)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)
        # The extra pane makes Qt's default size hint too narrow for writing.
        available = self.screen().availableGeometry()
        self.resize(min(1000, available.width() * 9 // 10), min(700, available.height() * 9 // 10))
        self.splitter.setSizes([SIDEBAR_WIDTH, 760])

        file_menu = self.menuBar().addMenu("&File")
        edit_menu = self.menuBar().addMenu("&Edit")
        view_menu = self.menuBar().addMenu("&View")
        self.show_sidebar_action = QAction("Show Sidebar", self)
        self.show_sidebar_action.setCheckable(True)
        self.show_sidebar_action.setChecked(True)
        self.show_sidebar_action.toggled.connect(self._set_sidebar_visible)
        view_menu.addAction(self.show_sidebar_action)
        view_menu.addSeparator()
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

        theme_menu = view_menu.addMenu("Color Theme")
        theme_group = QActionGroup(self)
        self.theme_actions: dict[str, QAction] = {}
        for name in THEMES:
            action = QAction(name, self)
            action.setCheckable(True)
            theme_group.addAction(action)
            theme_menu.addAction(action)
            action.triggered.connect(lambda _checked=False, theme=name: self._change_theme(theme))
            self.theme_actions[name] = action
        self.theme_actions[DEFAULT_THEME].setChecked(True)

        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        self._connect_document_signals(self.editor.document())

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
        self.profile_name = DEFAULT_PROFILE
        self._change_theme(DEFAULT_THEME)
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
        if level and any(
            block.blockFormat().property(QTextFormat.Property.BlockQuoteLevel) == 1
            and not block.textList()
            for block in formatting.affected_blocks(self.editor.textCursor())
        ):
            # A quoted heading cannot survive Qt Markdown. Leave quoted text untouched.
            self._after_formatting()
            return
        formatting.apply_block_style(self.editor, level, heading_point_size(self.editor, level))
        self._after_formatting()

    def _toggle_character(self, kind: str) -> None:
        formatting.toggle_character(self.editor, kind)
        self._after_formatting()

    def _toggle_list(self, style: QTextListFormat.Style) -> None:
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        if formatting.list_style(cursor) != style and any(
            block.blockFormat().headingLevel() for block in formatting.affected_blocks(cursor)
        ):
            # One action must normalize the heading and apply the list in one Undo step.
            formatting.apply_block_style(self.editor, 0, heading_point_size(self.editor, 0))
        formatting.toggle_list(self.editor, style)
        cursor.endEditBlock()
        self._after_formatting()

    def _toggle_quote(self) -> None:
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        formatting.toggle_quote(self.editor, heading_point_size(self.editor, 0))
        cursor.endEditBlock()
        self._after_formatting()

    def _after_formatting(self) -> None:
        self._sync_formatting()
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

    def _connect_document_signals(self, document: QTextDocument) -> None:
        """Keep window actions and title bound to the editor's current document."""
        document.undoAvailable.connect(self.undo_action.setEnabled)
        document.redoAvailable.connect(self.redo_action.setEnabled)
        document.modificationChanged.connect(self._update_title)

    def _update_title(self) -> None:
        name = "Untitled"
        if self.current_path is not None:
            path = self.current_path
            name = path.stem if path.suffix.lower() in (".md", ".markdown") else path.name
        modified = self.editor.document().isModified()
        self.setWindowTitle(f"{name}{' *' if modified else ''} — EZmd")

    def _change_profile(self, name: str) -> None:
        self.profile_name = name
        apply_profile(
            self.toolbar,
            self.editor,
            self.content_layout,
            self.style_selector,
            name,
            self.colors,
        )
        apply_sidebar_style(self.sidebar, self.splitter, name, self.colors)

    def _change_theme(self, name: str) -> None:
        self.colors = THEMES[name]
        self.setPalette(theme_palette(self.palette(), self.colors))
        self._change_profile(self.profile_name)

    def _collapse_sidebar(self) -> None:
        if self._sidebar_collapsed:
            return
        self._expanded_sidebar_width = self.sidebar.width()
        self._sidebar_collapsed = True
        self.sidebar_header.hide()
        self.sidebar_expand_button.show()
        self.sidebar.setFixedWidth(SIDEBAR_RAIL_WIDTH)
        # A fixed child width alone does not update QSplitter's reserved pane width.
        self.splitter.setSizes(
            [SIDEBAR_RAIL_WIDTH, max(1, self.splitter.width() - SIDEBAR_RAIL_WIDTH)]
        )
        self.editor.setFocus()

    def _expand_sidebar(self) -> None:
        if not self._sidebar_collapsed:
            return
        self._sidebar_collapsed = False
        self.sidebar.setMinimumWidth(SIDEBAR_MIN_WIDTH)
        self.sidebar.setMaximumWidth(SIDEBAR_MAX_WIDTH)
        self.sidebar_expand_button.hide()
        self.sidebar_header.show()
        self.splitter.setSizes(
            [
                self._expanded_sidebar_width,
                max(1, self.splitter.width() - self._expanded_sidebar_width),
            ]
        )
        self.editor.setFocus()

    def _set_sidebar_visible(self, visible: bool) -> None:
        if not visible and not self._sidebar_collapsed:
            self._expanded_sidebar_width = self.sidebar.width()
        self.sidebar.setVisible(visible)
        if visible and not self._sidebar_collapsed:
            self.splitter.setSizes(
                [
                    self._expanded_sidebar_width,
                    max(1, self.splitter.width() - self._expanded_sidebar_width),
                ]
            )
        self.editor.setFocus()

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
            "Documents (*.md *.markdown *.txt);;All Files (*)",
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
        if path.suffix.lower() in (".md", ".markdown"):
            # Parse separately so a load failure cannot discard the live document.
            loaded_document = QTextDocument(self.editor)
            # setMarkdown creates undo commands; opening a file is not a user edit.
            loaded_document.setUndoRedoEnabled(False)
            try:
                loaded_document.setMarkdown(text)
                markdown_whitespace.restore(loaded_document, text)
            except (RuntimeError, ValueError) as error:
                loaded_document.deleteLater()
                QMessageBox.critical(
                    self, "Could not open document", f"Could not open {path.name}: {error}"
                )
                return
            loaded_document.setModified(False)
            loaded_document.setUndoRedoEnabled(True)
            old_document = self.editor.document()
            old_document.undoAvailable.disconnect(self.undo_action.setEnabled)
            old_document.redoAvailable.disconnect(self.redo_action.setEnabled)
            old_document.modificationChanged.disconnect(self._update_title)
            self.editor.setDocument(loaded_document)
            # setDocument replaces the QTextDocument, so its signals no longer reach the window.
            self._connect_document_signals(loaded_document)
            self.undo_action.setEnabled(False)
            self.redo_action.setEnabled(False)
            self._sync_formatting()
        else:
            self.editor.setPlainText(text)
        self.current_path = path
        self.editor.document().setModified(False)
        self._update_title()
        self.editor.setFocus()

    def save_document(self) -> bool:
        path = self.current_path
        if path is None:
            filename, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save Document",
                "",
                "Documents (*.md *.markdown);;Text (*.txt);;All Files (*)",
            )
            if not filename:
                return False
            path = Path(filename)
            if not path.suffix:
                path = path.with_suffix(".txt" if selected_filter == "Text (*.txt)" else ".md")
        try:
            if path.suffix.lower() in (".md", ".markdown"):
                live = self.editor.document()
                text = markdown_whitespace.serialize(live)
                verification = QTextDocument()
                verification.setMarkdown(text)
                markdown_whitespace.restore(verification, text)
                if document_semantics(live) != document_semantics(verification):
                    raise ValueError("saving would change this document's text or formatting")
            else:
                text = self.editor.toPlainText()
            write_text(path, text)
        except (OSError, UnicodeError, RuntimeError, ValueError) as error:
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
