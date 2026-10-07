# File format

This document describes current production behavior on `main`.

## Markdown-backed documents

For `.md` and `.markdown`, Qt's native Markdown support is the file boundary:

    UTF-8 Markdown text
    → QTextDocument.setMarkdown(...)
    → restore EZmd whitespace encoding when present
    → normal visual QTextDocument editing
    → temporary whitespace encoding when necessary
    → QTextDocument.toMarkdown()
    → temporary parse + semantic verification
    → UTF-8 safe write

The normal user edits a visual document, not Markdown source.

EZmd guarantees the features exposed by its own formatting controls within the tested safe profile:
Paragraph/H1/H2/H3, bold, italic, strikethrough, top-level bullet and numbered lists, and
blockquotes. Unsupported combinations are normalized by the editor or rejected by Save verification
rather than silently written with changed meaning.

Qt may understand additional Markdown constructs, but those remain best-effort until EZmd
explicitly adopts them as product features.

## Whitespace preservation

Qt Markdown drops some leading spaces and empty paragraphs.

EZmd therefore uses one narrow persistence adapter:

- Save may clone the live document and encode otherwise-lost leading spaces or empty/whitespace-only
  paragraphs with reserved markers before calling Qt's Markdown writer.
- Open restores those markers after Qt parses the Markdown.
- Literal reserved markers are escaped.
- The live editor document is not rewritten merely to serialize a file.

This adapter is limited to whitespace preservation. It is not a custom Markdown parser or general
compatibility layer.

## Save verification

Before replacing a Markdown file, EZmd reparses the serialized Markdown into a temporary
`QTextDocument`, restores encoded whitespace, and compares supported meaning with the live
document.

The comparison covers visible text, heading level, list type, quote state, and
Bold/Italic/Strikethrough runs.

If verification would change supported meaning, Save fails and the existing file and live editor
state remain intact.

## Plain text

`.txt` remains plain text:

    Open → QTextEdit.setPlainText(...)
    Save → QTextEdit.toPlainText()

Rich formatting is not durable in a `.txt` file.

## Source spelling

EZmd does not promise byte-for-byte Markdown preservation. Qt may write equivalent Markdown
punctuation differently after Save.

The product promise is visible and semantic round-trip for supported features, not preservation of
the exact punctuation an external editor used.

## User-facing naming

Normal in-app language should say "document", not "Markdown document".

The editor does not expose Markdown punctuation as the normal writing surface. Where practical, the
window title displays the document name without advertising the `.md` or `.markdown` suffix.
Operating-system file dialogs may still display real filenames and extensions.

## Safety guarantees

- Invalid UTF-8 is reported instead of silently replacing bytes.
- A failed read does not destroy the document already open.
- A failed write must not truncate the previous file.
- A failed Save must not mark unsaved work clean.
- Opening Markdown must not leave conversion steps in user Undo history.
- Saving must not mutate the live cursor, selection, formatting, or Undo history.
- Paths with Unicode and spaces remain supported.
- Unsaved changes are confirmed before destructive New/Open/Close operations.

## Known acceptance debt

Build 03's Windows CI Markdown round-trip problem remains unresolved and intentionally deferred.
Do not weaken the semantic Save guarantee to hide that problem.
