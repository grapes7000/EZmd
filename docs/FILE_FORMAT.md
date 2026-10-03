# File format

This document separates current production behavior from the approved Build 03 target.

## Current behavior on main

Until Build 03 is implemented, EZmd treats .md, .markdown, and .txt as UTF-8 plain text.

Open:

    file bytes
    → UTF-8 text
    → QTextEdit.setPlainText(...)

Save:

    QTextEdit.toPlainText()
    → UTF-8
    → safe QSaveFile replacement

Writes normalize line endings to LF.

Build 02 rich formatting is therefore temporary editor state and does not yet survive save/reopen.

## Build 03 target

For .md and .markdown, Qt's native Markdown support becomes the file boundary:

    UTF-8 Markdown text
    → QTextDocument.setMarkdown(...)
    → visual QTextDocument editing
    → QTextDocument.toMarkdown()
    → UTF-8 safe write

The normal user does not edit Markdown source. The file format exists underneath the visual editor.

EZmd guarantees the features it exposes through its own editor controls, beginning with the Build 02 vocabulary: Paragraph/H1/H2/H3, bold, italic, strikethrough, bullets, numbered lists, and blockquotes.

EZmd does not promise universal compatibility with every Markdown extension. It also does not add a validator to reject unfamiliar syntax. Constructs outside the product's exposed feature set are best-effort Qt behavior until a future product feature explicitly adopts them.

.txt remains plain text in Build 03.

## Source spelling

Build 03 does not promise byte-for-byte Markdown preservation. Qt may write equivalent Markdown differently after Save.

The product promise is visible and semantic round-trip for EZmd-supported features, not preservation of the exact punctuation an external editor used.

## User-facing naming

Normal in-app language should say "document", not "Markdown document".

The editor must not expose Markdown punctuation as the normal writing surface. Where practical, the window title should display the document name without advertising the .md or .markdown suffix. Operating-system file dialogs may still display real filenames and extensions according to the platform and user settings.

## Safety guarantees

- Invalid UTF-8 is reported instead of silently replacing bytes.
- A failed read does not destroy the document already open.
- A failed write must not truncate the previous file.
- A failed save must not mark unsaved work clean.
- Opening Markdown must not leave conversion steps in user Undo history.
- Saving must not mutate the live cursor, selection, formatting, or Undo history.
- Paths with Unicode and spaces remain supported.
- Unsaved changes are confirmed before destructive New/Open/Close operations.
