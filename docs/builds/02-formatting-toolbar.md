# Build 02 — Formatting toolbar

**Status: complete and merged.**

## Goal

Make the native editor behave like a familiar visual writing tool while keeping the live document
small and native.

## Delivered

Toolbar controls:

- Paragraph / H1 / H2 / H3
- Bold
- Italic
- Strikethrough
- Bulleted list
- Numbered list
- Blockquote
- Undo / Redo

Formatting is stored as native `QTextDocument` state. Lists are real Qt lists. Headings use semantic
heading levels. Blockquotes use Qt blockquote state plus a presentation-only painted rail.

Character formatting works on selections and future typing. Toolbar state follows cursor/selection.
Formatting commands use native Undo/Redo history.

## Important boundary

Build 02 does **not** make formatting durable on disk. Save still writes plain text.

That limitation is intentional and visible in `docs/STATUS.md` and `docs/FILE_FORMAT.md`.

## Main production files

- `src/ezmd/ui/formatting.py`
- `src/ezmd/ui/main_window.py`
- `src/ezmd/ui/quote_editor.py`
- `src/ezmd/ui/visual_profiles.py`

The next persistence build must preserve the simplicity and directness of this editor rather than
replacing it with a second editing model.
