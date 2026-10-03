# Architecture

This document describes the code on main and the approved Build 03 boundary.

## Runtime

src/ezmd/app.py creates one QApplication and one MainWindow.

MainWindow owns the current file path, menus, toolbar, visual editor, unsaved-change flow, and New/Open/Save actions.

The editor is a QTextEdit subclass backed by Qt's single QTextDocument. There is no second editable document model.

## Production modules

- src/ezmd/core/files.py — UTF-8 reads and safe replacement writes with QSaveFile.
- src/ezmd/ui/main_window.py — window construction, actions, editor state, and file workflow.
- src/ezmd/ui/formatting.py — semantic formatting operations on the Qt document.
- src/ezmd/ui/quote_editor.py — paints the blockquote rail without storing presentation text.
- src/ezmd/ui/visual_profiles.py — presentation geometry and system-derived colors.
- src/ezmd/app.py — application entry point.

## Boundaries

- Core file I/O must not depend on UI code.
- Presentation code must not become the source of document meaning.
- User-visible document state lives in the Qt document, not in a shadow buffer.
- File writes must remain safe on failure.
- Normal editing must not depend on WebEngine, QML/Qt Quick, or network clients.
- Add a production module only when it has one clear responsibility that improves readability.

## Build 03 persistence boundary

Build 03 keeps the same single-document architecture.

For .md and .markdown:

    UTF-8 file text
    → QTextDocument.setMarkdown(...)
    → existing QTextEdit/QTextDocument editing
    → QTextDocument.toMarkdown()
    → existing safe UTF-8 write

This conversion happens at Open and Save only. Normal typing, cursor movement, formatting, Undo/Redo, and profile changes do not continually convert Markdown.

Build 03 must not add:

- a custom Markdown parser or serializer;
- a synchronized Markdown source buffer;
- a persistent AST;
- HTML as a hidden durable format;
- a second editable document model;
- a Markdown preview;
- a new dependency.

If a future product feature requires behavior Qt cannot represent safely, that problem must be demonstrated before a targeted adapter is considered.

## Change rule

Do not design infrastructure for a hypothetical future feature. Add the smallest thing required by the active build, then reevaluate with real behavior and tests.
