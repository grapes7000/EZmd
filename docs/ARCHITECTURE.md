# Architecture

This document describes the code that exists on `main` today.

## Runtime

`src/ezmd/app.py` creates one `QApplication` and one `MainWindow`.

`MainWindow` owns the current file path, menus, toolbar, visual editor, unsaved-change flow, and
New/Open/Save actions.

The editor is a `QTextEdit` subclass backed by Qt's single `QTextDocument`. There is no second
document model.

## Production modules

- `src/ezmd/core/files.py` — UTF-8 reads and safe replacement writes with `QSaveFile`.
- `src/ezmd/ui/main_window.py` — window construction, actions, editor state, and file workflow.
- `src/ezmd/ui/formatting.py` — semantic formatting operations on the Qt document.
- `src/ezmd/ui/quote_editor.py` — paints the blockquote rail without storing presentation text.
- `src/ezmd/ui/visual_profiles.py` — presentation geometry and system-derived colors.
- `src/ezmd/app.py` — application entry point.

## Boundaries

- Core file I/O must not depend on UI code.
- Presentation code must not become the source of document meaning.
- User-visible document state lives in the Qt document, not in a shadow buffer.
- File writes must remain safe on failure.
- Normal editing must not depend on WebEngine, QML/Qt Quick, or network clients.
- Add a production module only when it has one clear responsibility that improves readability.

## Current persistence

The production editor opens and saves plain text. Rich formatting exists only in the live
`QTextDocument`. Durable rich formatting is the next architecture decision, not an implemented
feature.

## Change rule

Do not design infrastructure for a hypothetical future feature. Add the smallest thing required by
the active build, then reevaluate with real behavior and tests.
