# File format

This document describes **current production behavior**, not a future format promise.

## Current behavior on main

EZmd currently treats `.md`, `.markdown`, and `.txt` as UTF-8 plain text.

Open:

```text
file bytes
→ UTF-8 text
→ QTextEdit.setPlainText(...)
```

Save:

```text
QTextEdit.toPlainText()
→ UTF-8
→ safe QSaveFile replacement
```

Writes normalize line endings to LF.

Build 02 rich formatting is therefore temporary editor state and does not survive save/reopen.

## Safety guarantees already implemented

- Invalid UTF-8 is reported instead of silently replacing bytes.
- A failed write must not truncate the previous file.
- A failed save must not mark unsaved work clean.
- Paths with Unicode and spaces are supported.
- Unsaved changes are confirmed before destructive New/Open/Close operations.

## Durable rich format

Not decided yet.

Markdown remains under consideration because it is portable, human-readable, and widely supported.
The project has also observed that Markdown implementations differ in feature coverage and
round-trip behavior. No parser, serializer, Markdown dialect, or compatibility layer is currently
part of production `main`.

The next Build 03 contract must define the durable format from evidence and product requirements
before implementation begins.
