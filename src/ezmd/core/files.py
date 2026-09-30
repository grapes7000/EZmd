"""Plain-text document I/O, independent of the window and its visual profile."""

from pathlib import Path

from PySide6.QtCore import QIODevice, QSaveFile


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    data = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    file = QSaveFile(str(path))
    # The fallback writes directly over the old file, losing the safe-replacement guarantee.
    file.setDirectWriteFallback(False)
    if not file.open(QIODevice.OpenModeFlag.WriteOnly):
        raise OSError(file.errorString())
    if file.write(data) != len(data):
        error = file.errorString()
        file.cancelWriting()
        file.commit()  # Discard the temporary file.
        raise OSError(error)
    if not file.commit():
        raise OSError(file.errorString())
