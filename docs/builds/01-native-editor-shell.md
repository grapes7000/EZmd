# Build 01 — Native editor shell

**Status: complete and merged.**

## Goal

Create the smallest trustworthy native writing application.

## Delivered

- PySide6 / Qt Widgets application shell.
- One `QTextEdit` document surface.
- File → New, Open, Save.
- UTF-8 reads.
- Safe replacement writes with `QSaveFile`.
- Unsaved-change confirmation.
- Window title reflects filename and modified state.
- Lab, QTemp, and Focus visual profiles.
- Linux, macOS, and Windows CI.

## Important boundary

Build 01 is plain text. It intentionally does not provide durable rich formatting, Markdown
conversion, search, sidebars, databases, networking, or WebEngine.

## Main production files

- `src/ezmd/app.py`
- `src/ezmd/core/files.py`
- `src/ezmd/ui/main_window.py`
- `src/ezmd/ui/visual_profiles.py`

Build 02 was allowed to build on this shell without weakening its file-safety behavior.
