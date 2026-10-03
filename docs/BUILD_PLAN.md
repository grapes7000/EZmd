# Build plan

EZmd is developed in small launchable slices. A build should add one visible capability, keep the application runnable, add focused tests, and stop.

## Completed

### Build 01 — Native editor shell

New/Open/Save, safe UTF-8 files, unsaved-change protection, native window, and visual profiles.

### Build 02 — Formatting toolbar

Paragraph/H1/H2/H3, bold, italic, strikethrough, bullet and numbered lists, blockquotes, and native Undo/Redo.

## Next

### Build 03 — Qt Markdown persistence

Make the existing visual document durable using Qt's native Markdown reader and writer.

The user-facing goal is deliberately simple:

> Open a document, work on it visually, save it, reopen it, and see the same supported content and formatting without needing to know that Markdown is involved.

Exact implementation and acceptance requirements are in docs/builds/03-qt-markdown-persistence.md.

Build 03 does not expand the toolbar, add Markdown syntax UI, add compatibility code for every Markdown flavor, or introduce another parser.

## Direction after Build 03

These are planning areas, not active implementation contracts.

### Desktop completeness pass

Before adding advanced knowledge-management features, make the application behave like a complete desktop editor. Candidate work includes normal editing commands, Save As, predictable shortcuts, recent/open flows, drag/drop where useful, links behaving naturally, clear feedback, sensible dialogs, and other small expectations discovered through real use.

This pass should be broken into small slices rather than one large rewrite.

### UI design and polish pass

Define a coherent visual and interaction system for the application.

Use Figma if useful to explore:

- overall window layout;
- toolbar/menu hierarchy;
- typography and spacing;
- sidebar/workspace layouts;
- empty states;
- dialogs and lightweight feedback;
- interaction flows.

Figma designs are references for the native Qt implementation, not a reason to introduce a web runtime or generated UI architecture.

### Workspace features

After the basic editor feels complete, add organization and navigation in small slices. Likely areas include:

- a simple collapsible and toggleable document sidebar;
- document navigation;
- full-text search;
- quick open;
- links and link navigation;
- backlinks or related-document features only when the simpler linking workflow exists first.

Do not implement these from this roadmap alone. Each receives its own precise build document when it becomes the next approved slice.
