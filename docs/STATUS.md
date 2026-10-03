# Project status

This file answers one question: **what is true in EZmd right now?**

## Completed

### Build 01 — Native editor shell

Complete and merged. The app can create, open, edit, and safely save UTF-8 text files with
unsaved-change protection.

### Build 02 — Formatting toolbar

Complete and merged. The live Qt document supports Paragraph/H1/H2/H3, bold, italic,
strikethrough, top-level bullet and numbered lists, blockquotes, and native Undo/Redo.

## Not completed

### Build 03 — Durable rich-document persistence

Not implemented on `main`.

Several Markdown experiments were performed outside the accepted production state. The old custom
Markdown implementation is obsolete and its pull request is closed. The later Qt-native experiment
was not committed to `main`.

The next persistence approach will be chosen after an explicit architecture discussion.

## Important current behavior

- `.md`, `.markdown`, and `.txt` files are currently opened as UTF-8 plain text.
- Save currently writes `editor.toPlainText()`.
- Build 02 visual formatting therefore does **not** survive save/reopen.
- The only production dependency is PySide6.
- Linux, macOS, and Windows are first-class targets.
- Qt Widgets is the current UI technology.
- There is no WebEngine, browser runtime, network client, database, plugin system, or Markdown parser
  in production code.

## Next decision

Before Build 03 resumes, decide the durable document format and the smallest safe open/edit/save
pipeline. No future build is authorized by this status document.
