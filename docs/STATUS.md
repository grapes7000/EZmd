# Project status

This file answers one question: what is true in EZmd right now?

## Completed

### Build 01 — Native editor shell

Complete and merged. The app can create, open, edit, and safely save UTF-8 text files with unsaved-change protection.

### Build 02 — Formatting toolbar

Complete and merged. The live Qt document supports Paragraph/H1/H2/H3, bold, italic, strikethrough, top-level bullet and numbered lists, blockquotes, and native Undo/Redo.

## Next approved slice

### Build 03 — Qt Markdown persistence

Implemented in the current working tree; owner manual acceptance and cross-platform CI are still
required before it can be called complete.

The slice uses Qt's native Markdown conversion, with one focused encoding for whitespace that
Qt would otherwise delete:

    Markdown file
    → QTextDocument.setMarkdown(...)
    → normal visual editing
    → QTextDocument.toMarkdown()
    → Markdown file

The user should open a document, work visually, save it, reopen it, and see the same supported
content and formatting without needing to know or interact with Markdown syntax. Save checks the
native Qt conversion before replacing a Markdown file and reports a failure if content or
formatting would change. Leading spaces and empty paragraphs are encoded on a temporary copy
and restored when the document is opened.

See docs/builds/03-qt-markdown-persistence.md for the exact contract.

## Important current behavior

Until Build 03 is accepted and merged:

- The in-progress Markdown implementation and its safety checks are in the working tree.
- The documented Build 03 safe formatting profile is tested locally but awaits owner acceptance.
- The only production dependency is PySide6.
- Linux, macOS, and Windows are first-class targets.
- Qt Widgets is the current UI technology.
- There is no WebEngine, browser runtime, network client, database, plugin system, or Markdown parser dependency in production code.

## After Build 03

The next work will move away from file-format experimentation and toward making EZmd feel like a complete, intuitive desktop application: desktop usability, stronger visual design, and then workspace features. Those directions are described in docs/BUILD_PLAN.md; they are not yet active implementation contracts.
