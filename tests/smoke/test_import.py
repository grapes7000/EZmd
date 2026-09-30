"""Cheap smoke coverage for the real application package."""

from pytestqt.qtbot import QtBot


def test_ezmd_package_imports() -> None:
    import ezmd

    assert ezmd.__name__ == "ezmd"


def test_real_main_window_initializes(qtbot: QtBot) -> None:
    from ezmd.ui.main_window import MainWindow

    window = MainWindow()
    qtbot.addWidget(window)
    assert window.editor.toPlainText() == ""
    assert window.current_path is None
    assert not window.editor.document().isModified()
