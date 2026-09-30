"""The one-document native writing window."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ezmd.core.files import read_text, write_text
from ezmd.ui.visual_profiles import DEFAULT_PROFILE, PROFILES, apply_profile, system_colors


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_path: Path | None = None
        self.editor = QTextEdit(self)
        self.editor.setAcceptRichText(False)
        self.editor.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoNone)

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

        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        document = self.editor.document()
        document.undoAvailable.connect(self.undo_action.setEnabled)
        document.redoAvailable.connect(self.redo_action.setEnabled)
        document.modificationChanged.connect(self._update_title)

        # The single separator intentionally keeps Qt's native platform geometry.
        self.toolbar.addSeparator()
        self.profile_selector = QComboBox(self.toolbar)
        self.profile_selector.addItems(list(PROFILES))
        self.profile_selector.setAccessibleName("Visual profile")
        self.toolbar.addWidget(self.profile_selector)
        self.colors = system_colors(self.palette())
        self.profile_selector.setCurrentText(DEFAULT_PROFILE)
        self.profile_selector.currentTextChanged.connect(self._change_profile)
        self._change_profile(DEFAULT_PROFILE)
        self._update_title()
        self.editor.setFocus()

    def _add_action(
        self, label: str, shortcut: QKeySequence.StandardKey, callback: Callable[[], object]
    ) -> QAction:
        action = QAction(label, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        self.toolbar.addAction(action)
        button = self.toolbar.widgetForAction(action)
        if isinstance(button, QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return action

    def _update_title(self) -> None:
        name = self.current_path.name if self.current_path is not None else "Untitled"
        modified = self.editor.document().isModified()
        self.setWindowTitle(f"{name}{' *' if modified else ''} — EZmd")

    def _change_profile(self, name: str) -> None:
        apply_profile(
            self.toolbar,
            self.editor,
            self.content_layout,
            self.profile_selector,
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
