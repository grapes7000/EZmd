# Build 02 — Word-like Formatting Toolbar

## Status

Ready for OpenCode Plan mode.

## Purpose

Turn the Build 01 text editor into a small, familiar rich-text editor without exposing Markdown
syntax to the user.

Build 02 proves the editable document model and formatting interactions. It deliberately does not
solve Markdown persistence yet; Build 03 owns rich document ↔ Markdown round-tripping.

## Settled decisions for this build

These are product/architecture decisions. OpenCode Plan mode must not reopen them.

- The primary editor remains the existing `QTextEdit` / `QTextDocument`.
- The approved Build 02 formatting vocabulary is:
  - Paragraph;
  - H1;
  - H2;
  - H3;
  - Bold;
  - Italic;
  - Strikethrough;
  - bulleted list;
  - numbered list;
  - blockquote.
- The formatting toolbar is compact and text-first.
- Its left-to-right grouping is:

  ```text
  ↶ ↷ | Paragraph ▾ | B I S | • 1. Quote
  ```

  The exact rendered glyph for strikethrough may make the `S` visibly struck through, but it
  remains the strikethrough control.
- Undo/Redo use familiar curved-arrow visual controls and the existing native Qt document undo
  history.
- New/Open/Save are removed from the formatting toolbar and remain available from the normal
  application menu bar.
- The top application menus are `File`, `Edit`, and `View`:
  - `File`: New, Open, Save;
  - `Edit`: Undo, Redo;
  - `View`: Visual Profile → Lab / QTemp / Focus.
- The visual-profile selector is no longer a formatting-toolbar control in Build 02.
- The normal native window title bar/chrome remains. Do not implement a custom title bar.
- Bold uses the platform-standard Bold shortcut (`Ctrl+B` on the common Windows/Linux mapping,
  `Cmd+B` on macOS through Qt standard-key handling).
- Italic uses the platform-standard Italic shortcut (`Ctrl+I` on the common Windows/Linux mapping,
  `Cmd+I` on macOS through Qt standard-key handling).
- Undo/Redo and New/Open/Save continue to use Qt standard shortcuts rather than hard-coded
  OS-specific key combinations.
- No new icon-pack dependency is allowed. Use a small verified Qt/system/native mechanism or a
  reliable text glyph for the curved Undo/Redo controls.
- Pasted content remains plain text in Build 02. Arbitrary external rich formatting must not enter
  the controlled document vocabulary through paste.
- Build 02 formatting is intentionally in-memory only. Saving continues to write Build 01 plain
  text; Build 03 adds durable Markdown formatting.

Read before planning:

- `AGENTS.md`
- `docs/DESIGN_PHILOSOPHY.md`
- `docs/ARCHITECTURE.md`
- `docs/UI_SYSTEM.md`
- `docs/FILE_FORMAT.md`
- `docs/PLATFORM_SUPPORT.md`
- `docs/HARDENING.md`
- `docs/TESTING.md`
- `docs/builds/01-native-editor-shell.md`
- `docs/decisions/001-native-qt.md`
- `docs/decisions/002-markdown-source-of-truth.md`
- `docs/decisions/003-no-webengine.md`
- `docs/decisions/006-qt-widgets-primary-ui.md`
- `docs/decisions/007-semantic-visual-profiles.md`
- `docs/decisions/008-cross-platform-desktop.md`

`docs/FUTURE_IDEAS.md` is context only. Its deferred ideas are not permission to implement them in
Build 02.

## OpenCode Plan-mode assignment

Plan **how to implement this contract cleanly**. Do not redesign the product or pull in deferred
features.

The plan must include:

1. the small set of source/test files expected to change;
2. the proposed responsibility of each changed/new source module;
3. how character formatting and block formatting will be applied through `QTextCursor` /
   `QTextDocument` without a second document model;
4. how toolbar checked/selected state will follow the cursor/selection without mutating the
   document or creating undo entries;
5. how one user formatting command becomes one logical undo step;
6. how real Qt list/block semantics will be used rather than fake text prefixes;
7. how the toolbar/menu actions share the same underlying `QAction` state where appropriate;
8. how the three visual profiles style the new controls without moving formatting semantics into
   visual-profile code;
9. the acceptance promises mapped to focused UI/integration/smoke/architecture tests;
10. Linux/macOS/Windows shortcut, menu, focus, font/glyph, and offscreen-test considerations;
11. the Qt APIs/signatures/behavior that should be verified before coding, especially heading,
    list, blockquote, cursor-format, and edit-block behavior;
12. an implementation-size sanity check.

OpenCode may choose local function/module names and the smallest readable implementation shape.
A small formatting helper module is acceptable if it keeps `main_window.py` understandable. Do
not create a formatting framework, controller hierarchy, command bus, registry, or plugin API.

## User-visible outcome

The app opens as the same fast native editor from Build 01, but the main writing toolbar now
contains familiar rich-text controls:

```text
↶ ↷ | Paragraph ▾ | B I S | • 1. Quote
```

A user can format selected text, set formatting for text they are about to type, format whole
paragraph blocks, create simple lists/quotes, use familiar keyboard shortcuts, and see the toolbar
follow the current document state.

The user does not need to know Markdown syntax.

## Allowed implementation

Use straightforward PySide6 Qt Widgets and the existing native document model.

Implementation may add only the responsibilities needed for:

- formatting actions and toolbar controls;
- character-format application/querying;
- block-style application/querying;
- simple list creation/toggling/conversion;
- simple blockquote toggling;
- synchronization from cursor/selection state back into toolbar controls;
- the menu-placement change described above;
- Build 02 tests.

Prefer plain functions and direct Qt APIs. A focused `ui/formatting.py`-style module is acceptable
if it owns formatting operations/query helpers and prevents `main_window.py` from becoming a pile
of formatting logic. It must not become a generalized editor service.

## Files/roots allowed to change

Build mode may change only:

- `src/ezmd/ui/**`;
- `tests/**`;
- this Build 02 document only for factual implementation/status notes after implementation.

If implementation genuinely requires changing another production root, dependency file, global
architecture document, or CI workflow, stop and explain why before editing it.

## Approved dependencies

No new dependencies.

Continue using the existing Python/PySide6 runtime and current development toolchain.

## Required behavior

### 1. Menu and toolbar placement

The normal application menu bar exposes:

- `File` → New, Open, Save;
- `Edit` → Undo, Redo;
- `View` → Visual Profile → Lab, QTemp, Focus.

The formatting toolbar must not contain New/Open/Save or the visual-profile selector.

The toolbar groups are, in order:

1. Undo, Redo;
2. separator;
3. Paragraph/H1/H2/H3 selector;
4. separator;
5. Bold, Italic, Strikethrough;
6. separator;
7. Bulleted list, Numbered list, Blockquote.

Undo/Redo are visually represented by familiar curved arrows and remain keyboard accessible with
an understandable accessible name/tooltip. Do not add a third-party icon package.

The existing `QAction` instances should be shared between menu/toolbar representations where the
same command appears in both places. Do not create separate competing action state.

### 2. Character formatting

Bold, Italic, and Strikethrough are toggle actions.

With a non-empty text selection:

- if the entire selected range already has the requested character format, activating the action
  removes that format from the selection;
- otherwise, activating the action applies the format across the whole selection;
- a mixed formatted/unformatted selection therefore becomes fully formatted on the first click;
- one toolbar/shortcut command should be one logical undo operation.

With no selection:

- activating Bold/Italic/Strikethrough changes the typing format at the insertion point;
- subsequently typed text receives that format;
- toggling the action back off returns future typing to the corresponding normal format.

Formatting commands must not replace the editor, create a second document, or manually re-create
plain text.

### 3. Paragraph/H1/H2/H3 block styles

The style selector contains exactly:

- Paragraph;
- H1;
- H2;
- H3.

Applying a style affects complete text blocks/paragraphs, not only selected characters.

- With no selection, the current block receives the chosen style.
- With a selection spanning multiple blocks, every selected block receives the chosen style.
- Applying a style across multiple selected blocks is one logical undo operation.

Use semantic `QTextDocument`/block-format information suitable for later Markdown serialization;
do not fake headings solely by setting a larger font and hoping Build 03 can infer intent.

When the current selection spans different block styles, the selector must not falsely claim that
the whole selection is one style. A small neutral/mixed display state is acceptable; it is not a
fifth document style the user can apply.

### 4. Bulleted and numbered lists

Bulleted and numbered list controls create real Qt document-list structure rather than inserting
literal bullet/number characters into the text.

For the current block or selected blocks:

- Bullet toggles a simple top-level bulleted list.
- Numbered toggles a simple top-level decimal numbered list.
- activating the currently active list type removes the list structure and returns the affected
  blocks to ordinary non-list blocks;
- activating the other list type converts the affected list to that type rather than nesting one
  list inside another;
- multi-block changes are one logical undo operation.

Nested lists, custom numbering schemes, indentation controls, and complex list continuation rules
are not required in Build 02.

### 5. Blockquote

Blockquote is a toggle applying semantic quote/block state to the current block or all selected
blocks.

- A normal block becomes a top-level quote block.
- A selected set of normal blocks becomes top-level quote blocks.
- If every affected block is already quoted, toggling removes quote state.
- Mixed quoted/unquoted selection becomes fully quoted on the first activation.
- Multi-block changes are one logical undo operation.

Use the simplest verified Qt block semantic that Build 03 can map deliberately to Markdown `>`.
Do not implement nested/multi-level quotes in Build 02.

### 6. Toolbar state follows the document

Toolbar state updates when the cursor/selection changes and after relevant edits.

At minimum:

- cursor inside bold text → Bold appears active;
- cursor inside italic text → Italic appears active;
- cursor inside struck text → Strikethrough appears active;
- cursor/selection in a single block style → style selector shows that style;
- cursor inside a bulleted list → Bullet appears active;
- cursor inside a numbered list → Numbered appears active;
- cursor inside a quote block → Quote appears active.

For a mixed character-format selection, a binary toolbar toggle may display unchecked/neutral, but
activating it must follow the mixed-selection rule above and apply the format to the whole
selection.

Synchronizing toolbar state must not:

- change document text or formatting;
- move the cursor;
- change the selection;
- change current path;
- mark a clean document modified;
- add undo commands.

### 7. Undo/Redo and keyboard shortcuts

Undo/Redo continue to operate on the single native Qt document history established in Build 01.
Do not create a second undo stack.

Required standard shortcut behavior:

- Bold → Qt/platform standard Bold shortcut;
- Italic → Qt/platform standard Italic shortcut;
- Undo → Qt/platform standard Undo shortcut;
- Redo → Qt/platform standard Redo shortcut;
- New/Open/Save retain their existing Qt/platform standard shortcuts.

No custom shortcut is required yet for Strikethrough, list, quote, or paragraph-style actions.

### 8. Paste remains controlled/plain

Build 02 does not import arbitrary source formatting from websites, office suites, or other rich
text sources.

Pasted material remains plain text, preserving the Build 01 safety behavior. Users apply EZmd's
approved formatting through the toolbar/shortcuts.

Preserving rich formatting on copy/paste is not a Build 02 promise.

### 9. Build 02 interim save/open behavior

This is an intentionally short-lived development milestone.

- Open remains Build 01 plain UTF-8 text loading; Markdown syntax is not parsed into formatting.
- Save remains Build 01 safe UTF-8 plain-text saving from the editor's textual content.
- Rich formatting created in Build 02 is not serialized in this build.
- Do not write Qt HTML, RTF, an opaque sidecar, hidden metadata, or invented Markdown conversion to
  preserve formatting early.
- Do not add a save blocker/warning solely because formatting is transient in this development
  slice.
- Build 03 immediately owns durable Markdown persistence for the approved rich-document subset.

Tests/docs must be explicit about this temporary boundary and must not claim formatting survives
close/reopen during Build 02.

### 10. Visual profiles

Lab, QTemp, and Focus remain the same semantic geometry/interaction profiles.

The new toolbar controls must inherit the existing profile system rather than introducing
unrelated pixel literals or a separate theme layer.

Switching visual profiles must preserve:

- document text;
- rich formatting;
- cursor/selection;
- current path;
- modified state;
- undo/redo history.

Visual-profile code owns presentation only; it must not own formatting semantics.

### 11. Cross-platform behavior

Linux, macOS, and Windows remain first-class targets.

- Use Qt standard key sequences when available.
- Do not assume one platform's menu rendering or child-widget count/order.
- Do not write tests that depend on exact rendered pixel geometry or platform menu internals.
- The curved Undo/Redo representation must remain understandable on all three targets.
- UI tests run offscreen in CI.

## Explicit non-goals

Build 02 must **not** implement:

- Markdown parsing/serialization or formatting persistence;
- underline;
- arbitrary font family or font size;
- text colors/highlights;
- text alignment controls;
- indentation controls;
- task lists/checkbox blocks;
- links;
- images;
- horizontal rules;
- tables;
- nested lists;
- nested blockquotes;
- Markdown typing shortcuts;
- automatic quote/bracket/parenthesis pairing;
- toolbar customization/reordering;
- persistent settings;
- custom title bar/window chrome;
- source/preview/split modes;
- side panels/docks/editor splits;
- plugin architecture;
- new network/background behavior;
- new dependencies.

Deferred ideas and their rationale live in `docs/FUTURE_IDEAS.md` rather than being silently kept
in conversational context.

## Acceptance promises and required tests

OpenCode may choose exact test function names. Tests should prove behavior, not mirror helper
implementation.

### Existing Build 01 regression promises

The complete existing Build 01 test suite continues to pass. In particular:

- safe New/Open/Save behavior remains intact;
- unsaved-change protection remains intact;
- file-write failure protection remains intact;
- profile switching remains state-safe;
- Linux/macOS/Windows architecture boundaries remain intact.

### UI behavior (`pytest-qt`)

Prove at least:

- File/Edit/View expose the settled commands without assuming platform-specific internal menu
  counts/order;
- New/Open/Save are no longer toolbar controls;
- visual-profile choice is available under View rather than occupying the formatting toolbar;
- toolbar groups appear in the settled semantic order;
- toolbar Undo/Redo are the same actions/history as menu Undo/Redo;
- Bold applies/removes formatting on selected text;
- Italic applies/removes formatting on selected text;
- Strikethrough applies/removes formatting on selected text;
- Bold/Italic/Strikethrough with no selection affect subsequently typed text;
- a mixed character-format selection becomes fully formatted when its action is activated;
- one formatting command can be undone/redone through the native history;
- Paragraph/H1/H2/H3 apply to whole current/selected blocks;
- block-style selector follows current block state and does not lie about a mixed block-style
  selection;
- Bullet creates real list structure, toggles off, and converts to Numbered;
- Numbered creates real list structure, toggles off, and converts to Bullet;
- Quote toggles semantic quote state on current/selected blocks;
- toolbar synchronization follows cursor movement without modifying the document or undo history;
- Bold/Italic/Undo/Redo standard shortcuts activate the intended actions;
- profile switching preserves rich formatting and native undo/redo history;
- pasted rich content does not import arbitrary external formatting.

### File/integration behavior

Using disposable files only:

- existing safe file tests remain green;
- formatting a document and saving still writes the same plain textual content in Build 02;
- the saved file does not contain Qt HTML/RTF/opaque rich-text data introduced by Build 02.

Do **not** add a Build 02 test claiming rich formatting survives close/reopen. That promise belongs
to Build 03.

### Architecture/boundary checks

Existing Build 01 boundaries remain enforced:

- no Qt WebEngine family;
- no Qt QML/Qt Quick family;
- no Qt Network/network-client imports for production behavior;
- core code does not depend on UI implementation.

Do not add brittle source-policing tests merely to force one helper/module decomposition.

## Manual acceptance pass

After automated tests pass, launch the real app and verify:

1. the top application area reads naturally as File / Edit / View plus the formatting toolbar;
2. the toolbar visually reads as `↶ ↷ | Paragraph ▾ | B I S | • 1. Quote`;
3. curved Undo/Redo controls are immediately recognizable;
4. `Ctrl/Cmd+B`, `Ctrl/Cmd+I`, Undo, and Redo feel normal;
5. selection formatting and typing-format behavior feel predictable;
6. moving through differently formatted text updates toolbar state without flicker or cursor jumps;
7. lists and quotes look like document structure rather than typed marker characters;
8. Lab/QTemp/Focus all keep the toolbar usable and visually distinct;
9. normal typing still feels immediate.

No screenshot-golden test is required.

## Performance constraints

- Normal keystrokes must not scan/reformat the whole document.
- Cursor/selection synchronization should query only the state needed for the current
  cursor/selection.
- Formatting commands operate only on the current/selected range/blocks.
- No timer, polling loop, background worker, document scan, network request, or global stylesheet
  rebuild is needed for Build 02 formatting.
- Startup work should remain effectively the same scale as Build 01.

## Data-safety constraints

- Existing Build 01 safe file replacement and unsaved-change protection remain unchanged.
- Automated tests use disposable documents/files only.
- Build 02 must not introduce a second hidden document copy or opaque persistence format.
- Plain textual content must continue to save through the established safe file path.
- Formatting is intentionally transient in this development slice and must be documented/tested as
  such until Build 03 makes it durable Markdown data.

## Expected implementation size

Keep the feature small enough to understand in one owner review session.

Expected shape, not a rigid quota:

- one small focused formatting helper module is reasonable;
- modest changes to `main_window.py` and `visual_profiles.py` are reasonable;
- roughly 150-350 new/changed production lines is a useful target;
- tests may be similar or larger because cursor/selection/undo behavior deserves explicit cases;
- if production changes approach a mini-framework or substantially exceed about 500 new/changed
  lines, stop and explain why before continuing.

## Definition of done

- [ ] Application launches.
- [ ] Settled File/Edit/View placement is implemented.
- [ ] Toolbar matches the settled command groups/order.
- [ ] Approved character/block/list/quote formatting works.
- [ ] Toolbar state follows cursor/selection without mutating document state.
- [ ] Standard Bold/Italic/Undo/Redo shortcuts work cross-platform through Qt.
- [ ] Existing Build 01 behaviors/tests remain green.
- [ ] Focused checks pass during implementation.
- [ ] `uv run --locked python bin/check.py` passes locally.
- [ ] Linux, macOS, and Windows CI passes.
- [ ] No unrelated file changed.
- [ ] No unauthorized dependency was added.
- [ ] No later/deferred feature was implemented early.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.

## Owner review questions

After OpenCode Build mode finishes, the owner should be able to answer:

1. Where are formatting operations implemented, and why is that module/file small enough to
   understand?
2. How does Bold/Italic/Strikethrough behave differently for a selection versus an insertion
   point?
3. How are Paragraph/H1/H2/H3 represented semantically instead of inferred from visual font size?
4. How are bullet/numbered lists represented as real document structure?
5. How is blockquote state represented so Build 03 can deliberately serialize it?
6. What makes one toolbar formatting command one undo operation?
7. How does toolbar state follow cursor/selection without modifying the document or undo history?
8. Where are standard shortcuts assigned, and why are they portable?
9. How are File/Edit/View actions shared with toolbar actions rather than duplicated?
10. Which test proves profile switching preserves rich formatting/history?
11. Which tests prove Build 01 file safety still works?
12. Is any code present only for auto-pairing, toolbar customization, panels, Markdown persistence,
    or another future feature? If yes, remove it from Build 02.
