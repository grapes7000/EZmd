# Build 03 — Markdown Round-trip

## Status

Implemented locally after owner confirmation that Build 02 and this contract were accepted. The
focused and full local test suites pass; owner visual review and Linux/macOS/Windows CI remain.

## Purpose

Restore EZmd's normal architecture after the deliberately temporary Build 02 in-memory formatting
slice.

Build 03 makes the controlled rich-document vocabulary durable as plain Markdown without exposing
Markdown syntax as the normal editing experience.

The editor remains the same native `QTextEdit` / `QTextDocument`. Markdown is the durable file
representation, not a second live editor, preview pane, hidden database, or parallel document
model.

The Build 03 experience must preserve the project's two primary product priorities: ordinary
writing remains blazingly fast, and opening/editing/saving Markdown remains intuitive to someone
who does not know Markdown syntax.

## User-visible outcome

A user can:

- open a supported `.md` document;
- see supported Markdown formatting as normal visual formatting in the editor;
- edit it with the existing Word-like Build 02 controls;
- save it;
- close and reopen it;
- get the same supported visible text and supported formatting back.

A user may also open a `.txt` file as a plain-text import. EZmd must not overwrite that `.txt` file
when the user presses Save. The first save of an imported text document creates a Markdown document
instead, using the original filename stem as the natural default.

The user never has to edit Markdown source to use this feature.

## Settled decisions for this build

These are product/architecture decisions. OpenCode Plan mode must not reopen them.

- Plain Markdown is the durable source of truth.
- The existing `QTextEdit` / `QTextDocument` remains the only editable in-memory document state.
- Build 03 supports exactly the Build 02 controlled formatting vocabulary:
  - Paragraph;
  - H1;
  - H2;
  - H3;
  - Bold;
  - Italic;
  - Strikethrough;
  - top-level bulleted lists;
  - top-level decimal numbered lists;
  - one level of blockquote.
- Paragraph/H1/H2/H3 is independent from the top-level structural state.
- A block may be either ordinary, bulleted-list, numbered-list, or blockquote structure; Bullet,
  Numbered, and Blockquote are mutually exclusive because that is the Build 02 document model.
- Heading + list and heading + blockquote combinations are valid and must round-trip.
- Supported inline Bold/Italic/Strikethrough combinations must round-trip.
- Quote + list is not a supported Build 03 structure even though general Markdown can express it.
- Markdown parsing occurs when a Markdown document is opened.
- Markdown serialization occurs when a document is saved.
- Normal typing, cursor movement, selection changes, toolbar synchronization, and ordinary
  formatting must not trigger whole-document Markdown parsing or serialization.
- No second persistent document model, source buffer, AST, sidecar, HTML file, RTF file, database
  record, or cache may become authoritative.
- Temporary local parsing/serialization data structures are allowed during an open/save operation
  if they keep the implementation small and readable. They must not become long-lived editor state.
- No new production dependency is approved for this build.
- Do not use `QTextDocument.setMarkdown()` / `toMarkdown()` as an unbounded shortcut that silently
  expands the supported vocabulary. If a Qt Markdown API is used internally, the implementation
  must still enforce this contract's controlled subset and data-safety rules.
- Exact original Markdown spelling is not preserved. Supported Markdown is normalized to EZmd's
  canonical form on save.
- Common equivalent spellings of supported meanings may be accepted on input, then normalized on
  save, when doing so remains small and unambiguous.
- Semantic round-trip is the promise: supported visible text, supported block meaning, supported
  inline formatting, and intentional blank paragraphs must survive.
- Literal Markdown-looking characters typed as ordinary text remain ordinary text. Save must escape
  them when necessary so reopen does not accidentally create formatting.
- An empty Markdown document is valid. Empty content must not be treated as an error.
- `.txt` is import-only in Build 03. EZmd's durable save format is `.md`.
- Links, images, task lists, code blocks, tables, horizontal rules, HTML, footnotes, front matter,
  nested lists, nested quotes, quote+list combinations, and other Markdown extensions are not
  promoted into document semantics in this build.
- Unsupported Markdown follows a **lossless-or-refuse** rule: if unsupported structure cannot be
  represented safely by the Build 03 document model, opening the file must fail clearly and leave
  the current document/path/modified state untouched rather than silently flattening or destroying
  that structure.
- Markdown typing shortcuts are not part of Build 03. Normal typing remains literal text; a future
  optional shortcut feature may convert recognized typing into the same semantic document state.

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
- `docs/builds/02-formatting-toolbar.md`
- `docs/decisions/001-native-qt.md`
- `docs/decisions/002-markdown-source-of-truth.md`
- `docs/decisions/003-no-webengine.md`
- `docs/decisions/006-qt-widgets-primary-ui.md`
- `docs/decisions/008-cross-platform-desktop.md`

`docs/FUTURE_IDEAS.md` is context only. Deferred ideas are not permission to add them to Build 03.

## OpenCode Plan-mode assignment

Plan **how to implement this contract cleanly**. Do not redesign the product, widen the Markdown
vocabulary, or pull later workspace features into this slice.

The plan must include:

1. the smallest source/test file set expected to change;
2. the responsibility of each changed/new source module;
3. the exact conversion boundary between Markdown text and the existing `QTextDocument`;
4. how parsing builds the supported semantic block/character state without creating a second live
   document model;
5. how serialization reads the current `QTextDocument` without mutating it or creating undo entries;
6. the canonical Markdown output rules and escaping strategy;
7. how supported inline combinations and heading+structure combinations round-trip;
8. how `.txt` import is kept distinct from `.md` open/save behavior;
9. how open/save failure leaves the user's current document/path/modified state safe;
10. how unsupported Markdown is detected early enough to refuse opening without damaging the
    current document;
11. how literal Markdown-looking ordinary text remains literal through save/reopen;
12. the acceptance promises mapped to focused pure conversion tests, file-integration tests, Qt/UI
    tests, smoke tests, and architecture guards;
13. Linux/macOS/Windows newline, path, dialog-filter, encoding, shortcut, and offscreen-test
    considerations;
14. the Qt APIs/format properties that should be verified before coding, especially heading level,
    list membership/style, `BlockQuoteLevel`, fragment character formats, document modified state,
    and undo-stack behavior;
15. an implementation-size sanity check.

OpenCode may choose local function/module names and the smallest readable implementation shape.

A focused Markdown conversion module is expected and may use small ephemeral value objects while an
open/save operation is running. Do not create a generalized document framework, repository layer,
controller hierarchy, visitor framework, command bus, plugin API, or background parser service.

## Files/roots allowed to change

Build mode may change only:

- `src/ezmd/core/**`;
- `src/ezmd/ui/**`;
- `tests/**`;
- `docs/FILE_FORMAT.md`;
- this Build 03 document for factual implementation/status notes after implementation.

If implementation genuinely requires changing another production root, dependency file, accepted
decision record, global architecture document, or CI workflow, stop and explain why before editing
it.

Status-only roadmap/README edits after owner acceptance are a separate documentation step and are
not permission to alter unrelated project documentation during implementation.

## Approved dependencies

No new production dependencies.

Continue using the existing Python/PySide6 runtime and development toolchain.

## Required behavior

### 1. Markdown documents open into the visual editor

Opening a supported `.md` file:

- reads UTF-8 through the existing safe file-operation path;
- validates that the file stays within the controlled Build 03 subset before replacing the current
  document;
- parses the controlled Build 03 Markdown subset;
- builds the corresponding semantic state in the existing `QTextDocument`;
- leaves the opened document clean/unmodified;
- leaves no synthetic parse operations available in the user's Undo history;
- updates the current path only after the complete open operation succeeds;
- preserves the previous document/path/modified state if reading, validation, or conversion fails.

The editor must show the final-looking document, not Markdown source punctuation for supported
constructs.

Opening must remain a deliberate file operation. Do not parse the entire document on every
keystroke merely to keep a source representation synchronized.

### 2. Supported block vocabulary

The following block meanings are durable:

- ordinary paragraph;
- H1;
- H2;
- H3;
- top-level bulleted list item;
- top-level decimal numbered list item;
- one level of blockquote.

Paragraph/H1/H2/H3 is independent from the structural choice. The structural choice is exactly one
of ordinary, Bullet, Numbered, or Blockquote.

The conversion design must deliberately support:

- ordinary paragraph;
- heading;
- top-level list item;
- top-level blockquote;
- heading + top-level list item;
- heading + top-level blockquote;
- any of those with supported inline formatting.

Quote + list is not supported because Build 02 normalizes those structures to one or the other.
Nested lists and nested blockquotes remain out of scope.

### 3. Supported inline vocabulary

The following character meanings are durable:

- Bold;
- Italic;
- Strikethrough.

They may occur alone or in combination.

Formatting boundaries may start/end at different positions. Serialization must produce
deterministic valid Markdown even when Qt character-format runs do not align perfectly with a
single pair of Markdown delimiters.

The round-trip promise is semantic equality, not preservation of the original delimiter spelling.

### 4. Canonical Markdown output

EZmd saves a deliberately small canonical Markdown dialect.

Canonical block markers are:

```text
# H1
## H2
### H3

- Bullet item

1. First numbered item
2. Second numbered item

> Quote
```

Each distinct contiguous numbered list serializes as a decimal sequence beginning at `1.` and
incrementing consecutively as `1.`, `2.`, `3.`, and so on. A separate list restarts at `1.`.

Canonical inline markers are:

```text
**bold**
*italic*
~~strikethrough~~
```

When supported inline styles overlap, output must use a fixed deterministic nesting/segmentation
rule and tests must prove that re-opening the saved Markdown reconstructs the same semantic
formatting.

A quoted heading is valid because heading style and quote structure are independent:

```text
> ## Heading
```

A heading list item is likewise valid when represented by the Build 02 document model. The exact
canonical ordering of the supported heading/list markers must be chosen deliberately, produce
valid readable Markdown, and round-trip in tests.

Do not emit quote+list combinations because the editor cannot produce that structural state.

The serializer must escape literal characters/sequences when necessary so ordinary text is not
accidentally reinterpreted as EZmd formatting on the next open.

At minimum, escaping must deliberately cover:

- backslash;
- literal emphasis/strikethrough delimiters;
- block-leading text that would otherwise become H1/H2/H3;
- block-leading text that would otherwise become a bullet;
- block-leading text that would otherwise become a numbered-list item;
- block-leading text that would otherwise become a quote.

Do not add an elaborate general-purpose Markdown escaping framework beyond what the supported
grammar needs.

### 5. Paragraphs, soft wrapping, and blank paragraphs

Canonical Markdown is semantic rather than source-layout preserving.

- One visual paragraph serializes as one logical Markdown paragraph.
- A normal paragraph that was soft-wrapped across multiple source lines may be normalized when
  opened/saved.
- Paragraph separation is represented with Markdown blank-line separation.
- Intentional empty/blank paragraphs created in the editor must survive save/reopen.
- A blank source line remains a block separator. A line containing exactly `\` canonically encodes
  one intentional empty ordinary paragraph; repeated empty paragraphs use repeated `\` blocks.
- Empty semantic blocks use bare markers: `#`/`##`/`###`, `-`, `1.` (or the next number in its
  list), and `>`. Combined empty heading structures use forms such as `- ##`, `1. ###`, and `> #`.
- Repeated source blank-line style is not preserved byte-for-byte unless it represents intentional
  blank paragraphs in the visual document.
- An empty document serializes as an empty file.
- A non-empty canonical document may use one final LF newline; whichever rule Plan mode chooses
  must be fixed, tested, and consistent across platforms.

Hard line-break syntax is not a Build 03 feature.

### 6. Supported Markdown import forms

The parser must accept EZmd's own canonical output.

For ordinary external Markdown, Build 03 accepts a small set of familiar equivalent spellings for
the same supported meanings without attempting to become a full CommonMark/GFM implementation.

At minimum accept:

- ATX `#`, `##`, and `###` headings;
- `-`, `*`, and `+` top-level bullets;
- decimal `N.` top-level numbered-list markers;
- one leading `>` quote level when it does not contain another structural state;
- `**...**` and `__...__` bold;
- `*...*` and `_..._` italic;
- `~~...~~` strikethrough;
- backslash escapes needed by EZmd's canonical serializer.

Equivalent spellings normalize to the canonical output in section 4.

Unmatched/incomplete supported delimiters that are unambiguously ordinary literal text must remain
visible literal text rather than deleting characters or throwing away the document.

Do not widen this into "support Markdown generally."

### 7. Unsupported Markdown: lossless or refuse

Build 03 is **not** a complete Markdown renderer.

Unsupported constructs include:

- links and autolinks;
- images;
- fenced/indented code blocks;
- inline code;
- task lists;
- tables;
- horizontal rules;
- YAML/front matter;
- HTML;
- footnotes;
- definition lists;
- nested lists;
- nested blockquotes;
- quote+list combinations;
- heading levels H4-H6;
- arbitrary Markdown extensions.

The rule is **lossless or refuse**.

If the source contains unsupported structure that EZmd cannot safely represent in the controlled
visual document model, Open must fail clearly and leave the currently open document, path,
modified state, cursor/selection, and undo history untouched.

Do not open unsupported structured Markdown as approximate plain text and then allow Save to destroy
or reinterpret that structure. Do not silently strip unsupported punctuation.

This rule does not make ordinary Markdown-significant punctuation unsupported. Text such as
`# literally a hash` or `**literal stars**` can exist as ordinary visual text when represented as
plain paragraph/characters; EZmd escapes it on save when necessary so it reopens literally.

Do not add a source pane, compatibility mode, hidden sidecar, opaque preservation metadata, or
second source buffer to work around this boundary. A later reviewed build may promote more
Markdown semantics into the controlled model.

### 8. `.txt` import

Opening `.txt` is an import operation, not a durable EZmd text-file mode.

Required behavior:

- read the text as UTF-8 through the safe existing file path;
- do **not** parse Markdown syntax from `.txt`;
- load all source characters as ordinary text;
- do not keep the `.txt` path as the active save target;
- treat the imported document as needing an EZmd save;
- Save therefore opens the normal save-path flow;
- default naturally to the source directory and source stem with `.md`;
- never overwrite the original `.txt` unless a future build explicitly creates an export feature.

The user's imported text remains fully editable before saving.

### 9. Save behavior

Saving an existing `.md` document:

- serializes the current supported `QTextDocument` state to canonical Markdown;
- writes UTF-8 using the established safe write path;
- uses LF line endings in the durable file;
- marks the document clean only after the write succeeds;
- keeps the document/path/modified state safe if serialization or writing fails.

Saving a new or imported document:

- asks for a destination using the existing save-path flow;
- uses Markdown as the durable file type;
- adds `.md` when the user supplies a filename with no suffix;
- must not silently save a new durable document as `.txt`.

If the user explicitly supplies a conflicting non-Markdown extension, the implementation must not
quietly create a durable format the app does not claim to support. Plan mode should choose the
smallest clear UX consistent with existing dialogs and tests.

Do not add autosave in Build 03.

### 10. New document behavior

A new document remains pathless until saved.

The user may create and save:

- ordinary text;
- formatted text;
- an entirely empty document.

The first durable save is Markdown.

### 11. Modified state and Undo/Redo

Open/parse and save/serialize are file-boundary operations, not user editing commands.

Required behavior:

- opening a document does not leave it modified;
- opening a document does not fill Undo with parser construction steps;
- saving does not add undo entries;
- serializing must not alter the current cursor/selection or rich document formatting;
- toolbar synchronization after open reflects the resulting document without mutating it;
- user edits after open continue to use the single native Qt undo history from Builds 01/02.

### 12. Visual profiles

Lab, QTemp, and Focus remain presentation-only.

Opening/saving/round-tripping must not depend on the active visual profile.

Switching visual profiles must continue preserving:

- document text;
- semantic formatting;
- cursor/selection;
- current path;
- modified state;
- undo/redo history.

The Build 02 quote hairline is presentation only and must not influence Markdown serialization.
`BlockQuoteLevel = 1` (or the verified equivalent semantic state) remains the quote meaning.

No Markdown rule belongs in visual-profile code.

### 13. Performance

Normal typing remains sacred.

Build 03 must not:

- serialize Markdown on each keystroke;
- reparse the whole document when the cursor moves;
- reparse the whole document merely to update toolbar state;
- keep a continuously synchronized Markdown source string;
- add a background parser/indexer service;
- add file watchers.

Open/save conversion may scale linearly with the one document being opened or saved.

For ordinary documents, the conversion should feel immediate. If profiling reveals a real issue,
optimize the measured hot path rather than adding speculative caching.

### 14. Cross-platform behavior

Linux, macOS, and Windows remain first-class targets.

- Read/write UTF-8 explicitly.
- Save canonical LF line endings independent of host OS.
- Use `pathlib`/Qt portable path behavior.
- Do not write tests that depend on one platform's file-dialog internals.
- Use disposable temporary files in tests.
- CI/offscreen tests must not require an interactive display.
- Native menu/shortcut behavior from Builds 01/02 must remain intact.

## Explicit non-goals

Build 03 must **not** implement:

- full CommonMark/GFM compliance;
- Markdown source mode;
- rendered preview mode;
- split source/preview mode;
- live Markdown source synchronization;
- HTML/RTF persistence;
- arbitrary rich-text paste preservation;
- links;
- images;
- inline code or code blocks;
- task lists;
- tables;
- horizontal rules;
- front matter;
- footnotes;
- H4/H5/H6;
- nested lists;
- nested blockquotes;
- quote+list structure;
- custom ordered-list starts;
- automatic Markdown typing shortcuts;
- automatic quote/bracket/parenthesis pairing;
- document sidebar;
- search;
- fuzzy Quick Open;
- wiki links/backlinks;
- graph view;
- autosave/recovery;
- persistent settings;
- plugin architecture;
- background services;
- new production dependencies.

## Acceptance promises and required tests

OpenCode may choose exact test function names. Tests must prove behavior rather than mirror helper
implementation.

### Pure Markdown conversion behavior

Prove at least:

- empty document -> empty Markdown -> empty document;
- plain paragraphs round-trip;
- H1/H2/H3 round-trip;
- Bold round-trips;
- Italic round-trips;
- Strikethrough round-trips;
- combined Bold/Italic/Strikethrough round-trip;
- formatting transitions within one paragraph round-trip;
- bulleted lists round-trip as real top-level list structure;
- numbered lists round-trip as real top-level decimal list structure;
- blockquote round-trips through `BlockQuoteLevel = 1` (or the verified equivalent used by Build
  02);
- quoted headings round-trip;
- heading list items round-trip if that is the verified Build 02 representation;
- headings/list items/quotes preserve supported inline formatting;
- literal Markdown-significant characters survive through escaping without becoming formatting;
- unmatched literal delimiters remain literal text;
- intentional blank paragraphs survive;
- canonical output is deterministic;
- saving canonical output, reopening it, and saving again is stable.

### Markdown normalization behavior

Prove at least:

- `__bold__` normalizes to canonical bold without changing meaning;
- `_italic_` normalizes to canonical italic without changing meaning;
- `*` and `+` top-level bullets normalize to canonical `-` bullets;
- ordered list source numbers normalize to EZmd's canonical sequence;
- line-ending input may normalize to LF;
- exact original delimiter spelling is not accidentally treated as a promise.

### Unsupported Markdown behavior

Using representative unsupported constructs, prove at least:

- a file with a link is refused rather than opened lossy;
- a file with an image is refused;
- fenced code is refused;
- a table is refused;
- nested list/quote or quote+list structure is refused;
- H4-H6 is refused;
- failed unsupported open preserves the previous document text, semantic formatting, path,
  modified state, cursor/selection, and undo history;
- rejection does not mutate the unsupported source file.

Do not attempt exhaustive CommonMark validation. The tests should cover each unsupported category
that the implementation explicitly detects and the safety invariant that refusal is non-destructive.

### `.txt` import behavior

Using disposable files only:

- `.txt` content loads as plain text even when it contains Markdown-looking characters;
- imported `.txt` does not become the active overwrite target;
- Save on an imported text document uses an `.md` destination;
- the source `.txt` remains unchanged;
- an empty `.txt` import is valid.

### File/integration behavior

Using disposable files only:

- opening valid `.md` creates the expected rich `QTextDocument`;
- open/read/validation/conversion failure preserves the previous document/path/modified state;
- opened Markdown starts clean;
- parser construction does not appear in user Undo history;
- saving an existing `.md` writes canonical UTF-8/LF Markdown;
- serialization failure/write failure preserves user work and dirty state;
- successful save marks the document clean;
- Save with a filename lacking a suffix produces `.md`;
- new empty document can be saved as an empty `.md`;
- close/reopen after Save reproduces supported semantics.

### UI behavior (`pytest-qt`)

Prove at least:

- File/Open can select the supported Markdown path without adding a source/preview UI;
- `.txt` import uses the same familiar editor but follows import-save semantics;
- toolbar state after Markdown open matches the parsed formatting;
- cursor/selection is not unexpectedly moved by a save;
- Save does not mutate formatting;
- Undo/Redo still operate only on user document edits;
- profile switching after Markdown open remains state-safe;
- no new always-visible Markdown controls are added;
- unsupported Markdown produces a clear user-facing failure without replacing the current document.

### Architecture/regression behavior

Prove at least:

- the existing Build 01/02 suite remains green;
- no new production dependency is added;
- no WebEngine/QML/JavaScript editor stack is introduced;
- no second persistent document/source model is introduced;
- no database/cache/sidecar becomes required for document fidelity;
- normal cursor/toolbar-state code does not invoke whole-document parse/serialize work;
- the full gate passes with `uv run --locked python bin/check.py`.

## Performance constraints

- Parsing/validation is open-time work.
- Serialization is save-time work.
- Normal typing/cursor/selection/toolbar synchronization must not perform full-document Markdown
  conversion.
- No polling or background watcher is added.
- No speculative cache is added.

If a design needs continuous source synchronization to work, stop: that design violates the Build
03 contract.

## Data-safety constraints

- Markdown files remain authoritative user data.
- Failed read, unsupported-syntax validation, or conversion must not destroy the currently open
  document.
- Failed save must not mark unsaved work clean.
- `.txt` import must not overwrite the source text file.
- Unsupported structured Markdown must be refused rather than silently flattened or deleted.
- Literal Markdown-looking ordinary text must remain literal through deliberate escaping.
- No hidden sidecar or derived store is required to reconstruct supported formatting.
- Conversion functions must be deterministic enough for focused round-trip tests.
- Tests use disposable files only.

## Cross-platform constraints

Linux, macOS, and Windows remain first-class targets.

Use portable Qt/Python behavior, explicit UTF-8, canonical LF output, and tests that do not depend
on platform-specific file-dialog internals or pixel rendering.

## Expected implementation size

The intended implementation is small enough to remain understandable to a beginner:

- one focused Markdown conversion responsibility in `core/` (possibly split into two tiny modules
  only if that is clearer);
- small file-boundary integration changes in the existing UI/window code;
- focused tests.

A rough expectation is:

- no more than 2–3 new production modules;
- no framework;
- no new dependency;
- no background worker;
- no persistent secondary model.

If Plan mode projects substantially more complexity, stop and identify which contract edge is
causing it before implementation begins.

## Definition of done

- [ ] Build 02 has been formally accepted/marked complete before Build 03 implementation starts.
- [ ] Application launches.
- [ ] Supported Build 02 formatting survives save/close/reopen through Markdown.
- [ ] `.txt` import -> `.md` save behavior works without modifying the source `.txt`.
- [ ] Empty Markdown documents work.
- [ ] Canonical output and escaping are deterministic.
- [ ] Literal Markdown-looking text remains literal after save/reopen.
- [ ] Unsupported structured Markdown is refused without replacing or mutating current user work.
- [ ] Open/save failure paths preserve user work.
- [ ] Normal typing does not perform Markdown conversion work.
- [ ] Focused checks passed during implementation.
- [ ] `uv run --locked python bin/check.py` passes.
- [ ] New required tests pass.
- [ ] No unrelated files changed.
- [ ] No unauthorized dependency was added.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.
- [ ] Owner visually verifies open/edit/save/reopen on a representative Markdown document.
- [ ] Cross-platform CI passes before Build 03 is marked complete.

## Owner review questions

When reviewing the Build 03 diff, answer:

1. Is the Markdown conversion code small enough to explain without a framework diagram?
2. Is `QTextDocument` still obviously the only editable in-memory document state?
3. Can any normal keystroke/cursor movement trigger whole-document parse/serialize work?
4. Does the serializer produce readable ordinary Markdown rather than an app-specific encoding?
5. Do all Build 02 formatting states have an explicit durable mapping?
6. Are literal Markdown-significant characters escaped deliberately rather than accidentally?
7. Does `.txt` import protect the original source file and save into `.md`?
8. Can a failed or unsupported open, or a failed save, leave user work in a worse state?
9. Is unsupported structured Markdown refused before the current document is replaced?
10. Did the implementation add abstractions, dependencies, caches, or background work that are not
    required by this slice?
11. Do the tests prove semantic round-trip instead of merely comparing implementation helpers?
12. Does the app still feel as immediate and familiar as Build 02?
