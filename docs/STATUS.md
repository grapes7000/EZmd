# Project status

This file answers one question: what is true in EZmd right now?

## Production `main`

### Build 01 — Native editor shell

Complete and merged. The app can create, open, edit, and safely save UTF-8 text files with
unsaved-change protection.

### Build 02 — Formatting toolbar

Complete and merged. The live Qt document supports Paragraph/H1/H2/H3, bold, italic,
strikethrough, top-level bullet and numbered lists, blockquotes, and native Undo/Redo.

### Build 03 — Qt Markdown persistence

Implementation is merged into `main` and is the production persistence baseline.

For `.md` and `.markdown`, EZmd uses Qt's native Markdown conversion, a narrow temporary
whitespace encoding for content Qt would otherwise delete, and strict semantic verification before
Save replaces a file. `.txt` remains plain text.

Build 03 is **not fully accepted** under its original completion rule because the Windows CI path
still exposes a Markdown round-trip problem and can time out after a Save failure dialog blocks in
offscreen CI. Linux and macOS passed. The owner has intentionally deferred the Windows
investigation; it remains known technical/acceptance debt rather than the active feature task.

See `docs/builds/03-qt-markdown-persistence.md` for the persistence contract.

## Active development — Build 04 Desktop workspace

Build 04 is one continuing desktop-workspace build. It intentionally combines:

- desktop shell and visual-system work;
- ordinary desktop-editor completeness;
- workspace/navigation features.

These are **not three sequential phases that must finish one at a time**. They may be interleaved
when that produces the simplest useful next slice. Every implementation change must still be small,
launchable, explicitly approved, and tested.

Current stacked development state:

- `build/04-01-design-tokens` adds Widgets-native spacing/radius/control tokens, a Compact visual
  profile, and built-in Light/Dark themes.
- PR #8, **Add editor-pane layout and collapsible sidebar shell**, has been merged into
  `build/04-01-design-tokens`. It moves the formatting toolbar into the editor pane and adds the
  resizable/collapsible/hideable Documents sidebar shell.
- That stacked Build 04 work is **not yet merged into `main`**.

Document navigation itself is not implemented by the sidebar-shell slice.

See `docs/builds/04-desktop-workspace.md` and `docs/UI_DIRECTION.md`.

## Current technology boundaries

- PySide6 is the only production dependency.
- Linux, macOS, and Windows remain first-class targets.
- Qt Widgets is the UI technology.
- The live Qt `QTextDocument` remains the editable document model.
- There is no WebEngine, browser runtime, network client, database, plugin system, or separate
  Markdown parser dependency in production code.
