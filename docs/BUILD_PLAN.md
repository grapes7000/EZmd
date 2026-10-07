# Build plan

EZmd is developed in small launchable slices. A build may describe a larger product direction, but
each implementation step should add one coherent capability, keep the application runnable, add
focused tests, and stop.

## Production baseline

### Build 01 — Native editor shell

New/Open/Save, safe UTF-8 files, unsaved-change protection, native window, and visual profiles.

### Build 02 — Formatting toolbar

Paragraph/H1/H2/H3, bold, italic, strikethrough, bullet and numbered lists, blockquotes, and native
Undo/Redo.

### Build 03 — Qt Markdown persistence

Merged into `main`. The existing visual document is durable through Qt's native Markdown reader
and writer, with narrow whitespace preservation and strict semantic Save verification.

Build 03's implementation is the production baseline, but its original acceptance checklist is not
fully closed because the Windows CI round-trip issue remains deferred. See
`docs/builds/03-qt-markdown-persistence.md`.

## Active — Build 04 Desktop workspace

Build 04 evolves EZmd from a durable one-document editor into a complete native writing workspace.

The owner treats the following as parts of the **same build**, not as mandatory sequential passes:

### Shell and visual system

- compact semantic design tokens and built-in themes;
- editor-pane ownership for the formatting strip;
- resizable/collapsible/hideable sidebar shell;
- centered page-like writing surface;
- application/menu hierarchy;
- development/status strip;
- continued visual polish discovered through use.

### Desktop completeness

Candidate slices include:

- normal editing commands;
- Save As;
- predictable shortcuts;
- recent/open flows;
- drag/drop where useful;
- links behaving naturally;
- clear feedback and sensible dialogs;
- other small desktop expectations found through real use.

### Workspace and navigation

Candidate slices include:

- document navigation inside the sidebar shell;
- full-text search;
- quick open;
- links and link navigation;
- backlinks or related-document features after the simpler linking workflow exists.

These areas may be interleaved. For example, a sidebar shell can be refined while Save As or a
small navigation capability is added. Do not wait for one category to be declared "finished" before
touching another if the next approved slice is smaller and more useful elsewhere.

## Current Build 04 implementation state

The active work is stacked off `main`:

1. **04.01 — design tokens/themes** on `build/04-01-design-tokens`.
2. **04.02 — editor pane + sidebar shell**, merged into that branch through PR #8.

The stacked branch is not yet production `main`.

No later candidate in this roadmap is automatically approved for implementation. The owner chooses
the next focused slice, and that task defines its exact behavior and acceptance criteria.

See `docs/builds/04-desktop-workspace.md` and `docs/UI_DIRECTION.md`.
