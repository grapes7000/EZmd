# Architecture

This document describes the in-progress Build 03 boundary and the one-document architecture.

## Runtime

src/ezmd/app.py creates one QApplication and one MainWindow.

MainWindow owns the current file path, menus, toolbar, visual editor, unsaved-change flow, and New/Open/Save actions.

The editor is a QTextEdit subclass backed by Qt's single QTextDocument. There is no second editable document model.

## Production modules

- src/ezmd/core/files.py — UTF-8 reads and safe replacement writes with QSaveFile.
- src/ezmd/ui/main_window.py — window construction, actions, editor state, and file workflow.
- src/ezmd/ui/formatting.py — semantic formatting operations on the Qt document.
- src/ezmd/ui/markdown_whitespace.py — narrow whitespace encoding at Markdown Open/Save.
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
    → restore any EZmd-encoded whitespace in the temporary document
    → existing QTextEdit/QTextDocument editing
    → optional temporary clone to encode otherwise-lost whitespace
    → QTextDocument.toMarkdown()
    → temporary QTextDocument.setMarkdown(...) and whitespace restoration
    → strict semantic verification
    → existing safe UTF-8 write

Save compares the temporary document's visible text, heading, list, quote, and inline runs with
the live document before calling the safe writer. Failed verification keeps the existing file
and the live document intact. Conversion happens at Open and Save only. Normal typing, cursor
movement, formatting, Undo/Redo, and profile changes do not continually convert Markdown.

Qt Markdown drops leading spaces and empty paragraphs. The approved narrow exception encodes
them in a temporary document with non-breaking spaces and a reserved invisible marker, tagged
with a file header. Open and Save verification decode those markers only in temporary parsed
documents. Literal markers are escaped. This does not parse general Markdown or modify the live
editor during conversion.

The formatting controls keep live editing in the tested safe Markdown profile: Paragraph may
use a top-level list or Quote, but not both. H1/H2/H3 are standalone, with neither list nor Quote.
Headings have Bold on and no Italic or Strikethrough. In Paragraphs, Strikethrough is exclusive
with Bold and Italic. A failed Save still protects any real text or formatting loss. Qt cannot
reliably preserve consecutive heading-list items or some adjacent quoted-list boundaries, so
those combinations are unavailable through the toolbar.

Build 03 must not add:

- a general-purpose Markdown parser or serializer;
- a synchronized Markdown source buffer;
- a persistent AST;
- HTML as a hidden durable format;
- a second editable document model;
- a Markdown preview;
- a new dependency.

The whitespace module is the one approved, limited exception to the native-only conversion
boundary. It must not grow into formatting or general Markdown compatibility code.

If a future product feature requires behavior Qt cannot represent safely, that problem must be demonstrated before a targeted adapter is considered.

## Change rule

Do not design infrastructure for a hypothetical future feature. Add the smallest thing required by the active build, then reevaluate with real behavior and tests.
