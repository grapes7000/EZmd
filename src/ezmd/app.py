"""Start the native EZmd application."""

import sys

from PySide6.QtWidgets import QApplication

from ezmd.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
