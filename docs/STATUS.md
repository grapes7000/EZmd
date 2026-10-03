# Project status

This file answers one question: what is true in EZmd right now?

## Completed

### Build 01 — Native editor shell

Complete and merged. The app can create, open, edit, and safely save UTF-8 text files with unsaved-change protection.

### Build 02 — Formatting toolbar

Complete and merged. The live Qt document supports Paragraph/H1/H2/H3, bold, italic, strikethrough, top-level bullet and numbered lists, blockquotes, and native Undo/Redo.

## Next approved slice

### Build 03 — Qt Markdown persistence

Specified and ready for implementation. It is not yet implemented on main.

The slice will use Qt's native Markdown conversion only:

    Markdown file
    → QTextDocument.setMarkdown(...)
    → normal visual editing
    → QTextDocument.toMarkdown()
    → Markdown file

The user should open a document, work visually, save it, reopen it, and see the same supported content and formatting without needing to know or interact with Markdown syntax.

See docs/builds/03-qt-markdown-persistence.md for the exact contract.

## Important current behavior

Until Build 03 is merged:

- .md, .markdown, and .txt files are still opened as UTF-8 plain text.
- Save still writes editor.toPlainText().
- Build 02 visual formatting therefore does not survive save/reopen.
- The only production dependency is PySide6.
- Linux, macOS, and Windows are first-class targets.
- Qt Widgets is the current UI technology.
- There is no WebEngine, browser runtime, network client, database, plugin system, or Markdown parser dependency in production code.

## After Build 03

The next work will move away from file-format experimentation and toward making EZmd feel like a complete, intuitive desktop application: desktop usability, stronger visual design, and then workspace features. Those directions are described in docs/BUILD_PLAN.md; they are not yet active implementation contracts.
