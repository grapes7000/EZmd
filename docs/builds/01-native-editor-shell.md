# Build 01 — Native Editor Shell

## Status

Implementation in review; local automated checks pass. Linux/macOS/Windows CI and on-screen
manual acceptance remain pending.

## Purpose

Create the smallest real EZmd application: a native cross-platform writing window that can edit,
open, and safely save plain text/Markdown files, while establishing the UI/testing/style
foundation later builds will extend.

This build intentionally proves the application's *shell and engineering discipline*. It does not
implement the rich Markdown editing model yet.

## Settled decisions for this build

These are product/architecture decisions. OpenCode Plan mode must not reopen them.

- Python minimum is 3.12.
- uv manages the environment/lockfile.
- PySide6/Qt 6 is the runtime UI dependency (`>=6.11,<7`).
- The primary UI uses **Qt Widgets**, not QML/Qt Quick.
- Qt WebEngine is forbidden from the core/primary UI.
- The central editor uses `QTextEdit`/`QTextDocument`.
- Linux, macOS, and Windows are first-class platform targets.
- pytest-qt is used for meaningful real-UI interaction tests.
- Visual values use a small semantic profile system rather than scattered hard-coded numbers.
- Build 01 exposes three live geometry/interaction profiles: `Lab`, `QTemp`, and `Focus`.
- `Focus` is the provisional startup profile; it is not a final visual-design verdict.
- The document occupies most of the window; controls remain compact and peripheral.

Read before planning:

- `AGENTS.md`
- `docs/DESIGN_PHILOSOPHY.md`
- `docs/ARCHITECTURE.md`
- `docs/UI_SYSTEM.md`
- `docs/PLATFORM_SUPPORT.md`
- `docs/HARDENING.md`
- `docs/TESTING.md`
- `docs/decisions/001-native-qt.md`
- `docs/decisions/003-no-webengine.md`
- `docs/decisions/006-qt-widgets-primary-ui.md`
- `docs/decisions/007-semantic-visual-profiles.md`
- `docs/decisions/008-cross-platform-desktop.md`

## OpenCode Plan-mode assignment

Plan **how to implement this contract cleanly**. Do not plan a new product architecture.

The plan must include:

1. the small set of source/test files you expect to add or change;
2. the proposed responsibility of each source module;
3. the document/file-action data flow from UI action to safe disk operation;
4. how modified/unsaved state will be represented without duplicating Qt state unnecessarily;
5. how semantic visual profiles will be represented/applied without creating a theme framework;
6. how the profile switcher will change visuals without changing document state;
7. the exact acceptance promises mapped to unit/integration/UI/smoke/architecture tests;
8. Linux/macOS/Windows path, shortcut, dialog, and headless-test considerations;
9. any PySide6 APIs whose behavior/signatures should be verified before coding;
10. an implementation-size sanity check.

The plan may choose local names, helper decomposition, and direct Qt APIs. It may improve the
*implementation shape* if it stays inside this contract.

Do not spend Plan mode proposing later formatting, autosave, sidebars, search, settings systems,
plugin/theme engines, or alternate GUI technologies.

## User-visible outcome

Running:

```text
uv run ezmd
```

opens one native desktop window with:

- a large central editable writing surface;
- a compact toolbar containing New, Open, Save, Undo, and Redo actions;
- standard menus exposing the same core actions where appropriate;
- a small visual-profile switcher for Lab / QTemp / Focus;
- a clear indication of the current file name and whether the document has unsaved changes.

The application should already feel like the skeleton of the final writing app rather than a test
harness.

## Allowed implementation

Use straightforward PySide6 Qt Widgets and normal Python.

The implementation may introduce only the small responsibilities required for:

- application startup/lifecycle;
- the main window and action wiring;
- one central `QTextEdit` writing surface;
- basic current-document state/path handling;
- safe UTF-8 open/save operations;
- unsaved-change protection;
- semantic visual-profile definitions/application;
- the Build 01 tests.

Prefer Qt/standard-library behavior over custom replacements. Use standard Qt shortcuts/actions
where they match the required behavior.

Do not create a generalized document framework, controller hierarchy, service layer, event bus,
settings subsystem, theme plugin system, or future-feature API.

## Files/roots allowed to change

Implementation may change only:

- `pyproject.toml` and `uv.lock` if dependency/entry-point metadata needs final adjustment within
  the already-approved dependency set;
- `src/ezmd/**`;
- `tests/**`;
- `.github/workflows/quality.yml` only if a real Build 01 Qt/cross-platform CI issue requires a
  narrow fix;
- this build document only for factual completion/status notes after implementation.

Do not revise project architecture/design documents during Build mode merely to match an
implementation choice. If the contract itself must change, stop and return to owner review first.

## Approved dependencies

Runtime:

- PySide6 (`>=6.11,<7`).

Development:

- existing uv/Ruff/BasedPyright/pytest/pytest-cov toolchain;
- pytest-qt.

No other runtime or development dependency may be added in Build 01.

## Required behavior

### 1. Launch and basic window

- `uv run ezmd` launches the application without network access.
- One normal native top-level window opens.
- The central `QTextEdit` is immediately usable for typing/selecting text.
- Build 01 treats editor content as plain text for persistence; rich formatted paste should not create a misleading unsaved format that cannot be written yet.
- The document/editor receives the majority of window space.
- The initial document is blank and has no associated path.
- The application must not create a document file merely by launching.

### 2. Toolbar and standard actions

Provide compact actions for:

- New;
- Open;
- Save;
- Undo;
- Redo.

Use standard Qt keyboard shortcuts where available so they map appropriately across operating
systems.

Undo/Redo operate on the actual central editor's undo history. Do not implement a second custom
undo stack for Build 01.

### 3. Modified/unsaved state

- Typing or editing after the last clean/load/save point marks the document modified.
- A visible window/title indication makes unsaved state understandable.
- Successful save/load/new resets modified state appropriately.
- Switching visual profiles must not affect modified state.

Prefer the Qt document's built-in modification state rather than maintaining a competing boolean
unless a narrow reason is documented.

### 4. New document

If the current document is clean:

- New clears the editor and removes the current file association.

If the document has unsaved changes:

- the user must be offered Save / Discard / Cancel before content is cleared;
- Cancel leaves text, selection/cursor, path, and modified state intact;
- Discard clears and starts a new untitled document;
- Save must complete successfully before clearing; a canceled/failed save aborts New.

### 5. Open document

- Open uses a normal Qt file picker.
- Build 01 accepts `.md`, `.markdown`, `.txt`, and an all-files option.
- The file is read as UTF-8.
- Opening a path containing spaces or non-ASCII characters must work.
- Successful open replaces the editor content, associates the path, and marks the document clean.
- The window clearly identifies the opened file.

If the current document is modified, Open uses the same Save / Discard / Cancel protection as New.
Cancel or failed save must leave the current document untouched.

If reading the chosen file fails, show an understandable error and leave the current document/path
untouched.

Build 01 does not parse Markdown when opening. It loads text into the native editor. Rich Markdown
conversion belongs to later builds.

### 6. Save document

If the document already has a path:

- Save writes the editor's current text to that file as UTF-8;
- successful save marks the document clean;
- failure shows an understandable error and leaves the in-memory document/path/modified state
  intact.

If the document has no path:

- Save asks for a destination through a normal Qt save dialog;
- canceling the dialog does nothing and leaves the document modified;
- a successful first save associates that path for later Save operations.

Saving must use a safe replacement strategy appropriate for desktop files so a failed write does
not intentionally truncate the previous file first. OpenCode may choose the simplest verified
Qt/standard-library mechanism that satisfies this promise.

Build 01 writes UTF-8 text with LF (`\n`) line endings on every platform. This is an intentional
portable baseline, not a promise to preserve an opened file's original newline style. Build 03 owns
the fuller Markdown round-trip/newline-preservation policy.

### 7. Close-window protection

Closing the application/window with unsaved changes uses the same Save / Discard / Cancel
semantics.

Cancel keeps the application open with the document unchanged. Failed/canceled save also prevents
closing.

### 8. Visual-profile system

The UI has exactly three Build 01 profiles:

- Lab;
- QTemp;
- Focus.

The measurements/intent are defined in `docs/UI_SYSTEM.md` and must be centralized in one small
visual-profile area.

Requirements:

- all user-facing spacing/radius/border/control-size values introduced for Build 01 come from
  semantic profile/palette definitions or Qt defaults with an explicit reason;
- do not duplicate three full widget trees;
- do not create separate main-window classes per profile;
- profile switching is live;
- switching does not alter document text, current path, selection/cursor, undo history, or modified
  state;
- no restart is required;
- persistence across application restarts is **not** required yet.

The Focus profile specifically includes quiet toolbar/action buttons whose resting state has no
visible outline. Hover introduces a restrained hairline outline and/or subtle surface change.
Keyboard focus must remain visible even when the mouse-resting state is borderless.

No profile should introduce decorative drop shadows in Build 01.

### 9. Cross-platform behavior

The same source implementation must work on Linux, macOS, and Windows.

- Do not construct paths by string concatenation/splitting.
- Do not assume `/` or `\\` separators.
- Do not shell out for file operations.
- Do not use OS-specific keyboard shortcuts when Qt standard shortcuts exist.
- UI tests must run offscreen in the CI matrix.
- File tests use pytest temporary directories, including at least one Unicode/space-containing path.

### 10. Error behavior

Expected user-caused I/O failures should produce a small understandable dialog/status outcome,
not a traceback in normal UI use.

Do not catch `Exception` broadly around large sections of the application merely to keep it
running. Catch narrow expected failures at the relevant I/O boundary.

## Explicit non-goals

Build 01 must **not** implement:

- rich-text formatting controls beyond Qt's native editable behavior;
- Markdown parsing or Markdown serialization rules;
- source/preview/split modes;
- Qt WebEngine;
- QML/Qt Quick;
- document sidebar/folder browser;
- full-text search or Quick Open;
- wiki links/backlinks;
- graph view;
- autosave/recovery/history database;
- recent-files list;
- persistent app settings or profile preference;
- custom title bar/window chrome;
- icon packs or icon dependency;
- animations;
- user-authored/importable themes;
- plugin architecture;
- background workers/services;
- network access/telemetry;
- executable packaging/installers.

## Acceptance promises and required tests

OpenCode may choose exact test function names, but the resulting suite must make these promises
obvious.

### Smoke

- the real `ezmd` package imports;
- the application/main-window path can be initialized safely in the test environment.

### UI behavior (`pytest-qt`)

- the main window contains one usable central text editor;
- typing through the editor marks the document modified;
- Undo/Redo actions affect actual typed text;
- activating New on a clean document produces a blank untitled clean document;
- Canceling the unsaved-change prompt prevents New from discarding text;
- Canceling the unsaved-change prompt prevents Open from discarding text;
- Canceling close with unsaved changes keeps the window/document alive;
- all three profiles can be selected at runtime;
- switching profiles preserves text and important document state;
- Focus quiet buttons have a distinguishable hover/focus rule without relying on a permanent
  visible border.

### File/integration behavior

Using real files under `tmp_path`:

- saving an untitled document to a chosen path writes the current UTF-8 text;
- later Save writes to the same associated file;
- opening a UTF-8 file loads its text and path and marks the document clean;
- paths containing spaces and non-ASCII characters work;
- canceling a save destination leaves disk/document state unchanged;
- a simulated/read failure does not replace the current document;
- a simulated/write failure does not mark the document clean or destroy the in-memory text.

### Architecture/boundary checks

Keep these small and readable:

- production code does not import Qt WebEngine;
- production code does not import Qt QML/Qt Quick modules for the primary UI;
- Build 01 contains no network-client dependency/import;
- visual profile definitions are centralized rather than duplicated into separate windows.

Do not write brittle source-policing tests for ordinary formatting/style choices.

## Manual acceptance pass

After automated tests pass, launch the real app and verify:

1. typing feels immediate;
2. New/Open/Save/Undo/Redo are understandable without reading documentation;
3. unsaved-change cancellation really preserves the work;
4. each profile visibly changes density/shape while the same text remains untouched;
5. Focus feels text-first and low-chrome;
6. window resizing does not make the editor or toolbar obviously unusable.

No screenshot-golden test is required in Build 01.

## Performance constraints

- No timer/polling/background work is needed for ordinary Build 01 editing.
- Normal keystrokes must not apply/rebuild the global stylesheet.
- Visual profiles are applied only when selected/startup requires it.
- Opening/saving touches only the selected/current file.
- Startup performs no scanning, indexing, network access, or model loading.

## Data-safety constraints

- Automated tests never touch real user files/configuration.
- Unsaved text cannot be discarded by New/Open/Close without an explicit Discard decision.
- A canceled/failed save is not treated as successful.
- A failed open does not replace the current in-memory document.
- A failed save does not intentionally truncate the old file before the replacement is ready.

## Expected implementation size

Keep this small enough for the owner to read in one review session.

Expected shape, not a rigid quota:

- roughly 4-7 focused production modules at most;
- roughly 250-500 lines of production Python for Build 01 is a reasonable target;
- tests may be similar in size because real UI/file failure behavior deserves explicit coverage;
- no single module should become a mini-framework or absorb unrelated future responsibilities.

If satisfying this contract appears to require substantially more machinery, stop and explain the
reason before building that machinery.

## Definition of done

- [ ] `uv run ezmd` launches the native Qt Widgets editor.
- [ ] Required user-visible behavior works.
- [ ] Required UI/integration/architecture/smoke promises are covered by readable tests.
- [ ] Focused checks passed during implementation.
- [ ] `uv run --locked python bin/check.py` passes locally.
- [ ] Linux, macOS, and Windows CI passes.
- [ ] No later feature was implemented early.
- [ ] No unauthorized dependency was added.
- [ ] No QML/Qt Quick or WebEngine primary-UI code was introduced.
- [ ] Visual measurements are centralized through the semantic profile system.
- [ ] No unrelated files changed.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.

## Owner review questions

After OpenCode Build mode finishes, the owner should be able to answer:

1. Which file starts the application?
2. Which file creates/composes the main window?
3. Where does file opening/saving happen, and how does it avoid destructive failure?
4. What is the one source of truth for "modified" state?
5. Where are Lab/QTemp/Focus measurements defined?
6. How does switching a profile avoid rebuilding/replacing the document?
7. Which tests prove unsaved work cannot be silently discarded?
8. Which tests prove actual Qt interaction instead of only helper functions?
9. What prevents a Linux-only path/shell assumption from slipping in?
10. Is there any class/module that exists only for a future feature? If yes, remove it.
