# Future Ideas & Open Questions

## Purpose

This document is the durable parking lot for product ideas, design context, and deferred decisions
that matter but are **not authorized by the currently active build slice**.

Its job is to prevent useful reasoning from living only in chat history or memory.

Nothing in this file is permission for a coding agent to implement a feature early. When an idea
becomes part of an active numbered build, its exact behavior must be promoted into that build's
reviewed contract first.

## How to use this document

Each item should capture:

- the user-facing idea;
- why it seems useful;
- decisions already made;
- important edge cases/risks already discovered;
- what still needs to be decided;
- likely timing/dependencies when known.

Keep the implementation architecture deliberately light until the relevant build proves that more
machinery is needed.

---

## Smart pair insertion

### Idea

Typing an opening delimiter can automatically insert the matching closer and leave the cursor
between the pair, for example:

```text
(|)
[|]
{|}
"|"
```

This is intended as small writing/editor polish rather than an IDE feature.

### Accepted direction so far

- Pairing is desirable for `(` / `)`, `[` / `]`, `{` / `}`, and likely double quotes.
- If implemented, pairing should probably be enabled by default but user-disableable.
- Typing a closer when the cursor is immediately before the automatically inserted matching closer
  should likely move past it rather than insert a duplicate.
- Wrapping an existing selection when an opener is typed is attractive and should be evaluated.
- The single quote/apostrophe (`'`) should **not** be blindly auto-paired.

### Why single quote is excluded from naive pairing

Ordinary prose uses apostrophes heavily inside words and dates, for example:

```text
don't
writer's
'90s
```

Automatically turning every `'` into `''` would be irritating and would make a writing-first app
behave like an over-eager code editor.

If apostrophe-aware quote behavior is ever added, it needs its own context rules rather than being
lumped into the simple delimiter-pair feature.

### Open questions

- Should double quotes always pair, or should they also become context-aware for prose?
- Should typing an opener around a selection wrap the selection for every supported pair?
- How should Backspace behave immediately inside an untouched empty pair?
- Should pair insertion interact with Markdown markers such as backticks, `*`, or `_`? Do not
  decide this before Markdown editing semantics are stable.
- Where should the preference live once persistent settings exist?

### Timing

Not Build 02. Revisit after the rich-document/Markdown model is stable and a small persistent
settings mechanism has a real use case.

---

## Customizable formatting toolbar

### Idea

Let the user enter a toolbar-edit mode and customize which formatting/actions appear and in what
order.

Desired user capabilities include:

- add an available action;
- remove an action from the toolbar without disabling the command itself;
- reorder actions;
- possibly insert/remove separators;
- restore the default layout.

### Accepted direction so far

- This fits EZmd's preference for modular, user-tailorable desktop interfaces.
- It should customize the existing action set rather than create duplicate command logic.
- Build 02 should create normal reusable `QAction` objects for commands so later customization can
  choose which actions are visible and where.
- Do **not** build a toolbar registry/framework in Build 02 merely for future customization.
- Restore Defaults is required whenever this feature is implemented.

### Why it is deferred

A genuinely customizable toolbar requires decisions that do not belong to initial formatting:

- stable identities for actions;
- layout persistence;
- separator representation;
- what happens when a future EZmd release adds/removes/renames actions;
- keyboard-accessible customization UX;
- interaction with visual profiles;
- migration/fallback for an invalid saved layout.

Those questions are easier to answer after the real toolbar has matured.

### Open questions

- Drag-and-drop editing versus a simple customize dialog/palette.
- Whether menus themselves become customizable (not currently requested).
- Whether hidden toolbar actions should always remain reachable through menus/shortcuts.
- Exact persisted representation once settings storage exists.

### Timing

After the formatting toolbar and workspace shape are stable enough that users are customizing a
real interface rather than a moving target.

---

## Modular workspace, side panels, and editor splits

### Idea

EZmd should eventually feel modular in the way the owner likes in VS Code, Zed, Obsidian, and
`lab-workspace`: one clean main editor can stand alone, while optional side/bottom panels or split
editor views can be opened when useful.

Examples:

- document/folder sidebar;
- search panel;
- backlinks panel;
- outline/connections panel;
- graph or other supporting views later;
- horizontal/vertical editor splits.

### Accepted direction so far

- A modular UI does **not** imply a plugin framework.
- Prefer Qt's existing lightweight desktop primitives first:
  - `QMainWindow` as the shell;
  - `QDockWidget` for hideable/movable side or bottom panels when appropriate;
  - `QSplitter` for resizable editor/workspace splits when appropriate.
- Start with explicit widgets/panels owned by the application. Do not invent `PanelManager`,
  `PluginHost`, `ExtensionRegistry`, dependency injection, or a generalized feature API before
  repeated real needs exist.
- The likely sequencing is after Build 03 establishes reliable rich-document ↔ Markdown behavior,
  so workspace layout cannot accidentally become entangled with document persistence.
- The existing Build 04 document-sidebar slice is a likely place to introduce the smallest useful
  workspace/panel structure, but Build 04 has **not** yet been amended to promise that. Decide when
  its contract is reviewed.

### One document, multiple views

A promising split-editor direction is multiple `QTextEdit` views sharing one `QTextDocument` rather
than maintaining synchronized duplicate text buffers.

Potential advantages:

- one document state;
- one source of truth for formatting/content;
- no manual text synchronization;
- two views can show different scroll positions into the same note.

Before adopting this, verify Qt behavior for:

- undo/redo across multiple views;
- cursor/selection ownership per view;
- focus and typing format;
- document lifetime;
- modified state;
- performance.

Do not assume the idea is correct merely because Qt appears to support sharing a document.

### Open questions

- Whether Build 04 should formally become “Modular workspace + document sidebar.”
- Whether docks should be movable/floating or only show/hide/resizable initially.
- Whether workspace layout persistence belongs with the first panels or a later preferences slice.
- How editor splits interact with opening different notes versus two views of one note.
- Minimum panel abstraction, if any, once several real panels exist.

---

## Deferred Markdown-capable formatting features

These are desirable candidates, but each introduces persistence/document-model questions beyond
Build 02's initial formatting vocabulary.

### Task lists

Desired eventually because they are useful in notes.

Need to decide:

- visual checkbox representation;
- whether checkboxes are clickable in the editor;
- mapping to `- [ ]` / `- [x]` Markdown;
- interaction with ordinary bullet lists;
- keyboard/accessibility behavior.

Do not implement as fake textual prefixes unless the relevant build explicitly chooses that model.

### Ordinary links

Desired eventually, but must be designed alongside later wiki-link behavior rather than painted
into a corner.

Need to decide:

- creating a link from selected text versus inserting new linked text;
- editing/removing an existing link;
- click versus Ctrl/Cmd-click behavior while editing;
- URL validation/escaping;
- how ordinary Markdown links coexist cleanly with later `[[wiki links]]`.

### Images

Desired eventually, but file/path semantics matter.

Need to decide:

- relative versus absolute paths;
- what directory relative paths are relative to;
- behavior for missing/moved files;
- drag/drop/paste image policy;
- whether resizing is stored and how that relates to portable Markdown;
- external URLs versus local files.

### Horizontal rules

Visually simple, but semantically a block/document object rather than character formatting.
Define its editable representation and Markdown round-trip deliberately before adding it.

### Tables

Potentially useful, but Qt rich-text tables and Markdown tables create a substantially larger
editing/round-trip problem than ordinary emphasis/headings/lists.

Need to decide the deliberately supported table subset before implementation. Avoid growing EZmd
into a spreadsheet/desktop-publishing system.

---

## Formatting intentionally not promised

The following common word-processor controls may conflict with EZmd's portable-Markdown identity
and should not be added merely because `QTextDocument` can represent them:

- arbitrary font families;
- arbitrary font sizes;
- arbitrary text colors/highlights;
- paragraph alignment;
- publication/page layout controls.

These are not necessarily permanently forbidden, but each needs a clear portable persistence story
or an explicit product decision about non-Markdown metadata before it becomes user-facing.

Underline is also deliberately absent from the initial controlled subset because ordinary Markdown
has no standard underline representation.

---

## Application menus and window chrome

### Accepted current direction

- Keep normal native window chrome/title bars.
- Use the normal application menu area for `File`, `Edit`, and `View`.
- From Build 02 onward:
  - New/Open/Save belong under `File` rather than occupying formatting-toolbar space;
  - Undo/Redo are under `Edit` and also appear as familiar curved-arrow controls in the formatting
    toolbar;
  - Lab/QTemp/Focus selection belongs under `View > Visual Profile` rather than occupying the
    formatting toolbar.

### Deferred

A custom title bar/window chrome is not currently justified. Cross-platform native behavior and
simplicity are more valuable than using title-bar space as a custom control strip.

Revisit only if a concrete later UX need cannot be met cleanly by the native menu/toolbar/dock
system.

---

## Settings/preferences

Several deferred ideas now have a real eventual need for persistent preferences:

- smart-pair insertion on/off;
- custom toolbar layout;
- possibly visual-profile choice;
- possibly workspace/panel layout.

This is useful evidence that a small settings mechanism will eventually be justified, but it is
**not** permission to build one early.

When the first persistent preference becomes an active build requirement, choose the smallest
cross-platform storage mechanism that satisfies the actual set of settings. Do not create a
settings framework for hypothetical options.

---

## Rule for promoting an idea into a build

Before implementation:

1. decide the exact user-visible behavior;
2. resolve the relevant open questions above;
3. amend the appropriate numbered build (or deliberately add a new slice);
4. define acceptance promises/non-goals/data/platform constraints;
5. only then allow OpenCode Plan mode to design the implementation.
