# Build 03 — Qt-native Markdown round-trip

## Status

Build 02 is complete and merged.

The previous Build 03 custom-parser direction is discarded. Build 03 now starts with the smallest
possible Qt-native Markdown integration so the project can observe what Qt 6.11 already does before
adding compatibility code.

The first implementation pass is intentionally experimental and narrow. No custom Markdown parser,
serializer, validator, dialect, allowlist, denylist, or normalization layer is authorized in that
pass.

## Purpose

Make Markdown formatting durable using the Markdown support already built into Qt.

Build 03 should first prove the simplest architecture:

```text
Markdown file
    ↓ open
QTextDocument.setMarkdown(...)
    ↓
existing visual editor
    ↓ save
QTextDocument.toMarkdown(...)
    ↓
Markdown file
```

EZmd should own the editor experience and safe file boundary, not reimplement Markdown.

The project will observe native Qt behavior first. Only demonstrated gaps may justify additional
code afterward.

## Product rule

**Native support is the default.**

If Qt can parse, represent, edit, and serialize a Markdown construct safely through the existing
`QTextDocument`, EZmd should not add code merely to reject or redefine that construct.

A Markdown feature should receive EZmd-specific handling only when testing demonstrates a concrete
problem such as:

- information is lost on save;
- the visual document cannot represent the meaning safely;
- editing silently corrupts or changes the meaning;
- behavior is materially inconsistent across supported platforms;
- the feature conflicts with an explicit EZmd product decision.

Do not create restrictions in anticipation of hypothetical problems.

## Settled architecture

- Plain Markdown remains the durable document format.
- The existing `QTextEdit` / `QTextDocument` remains the only editable in-memory document state.
- Use Qt's native Markdown conversion APIs first:
  - `QTextDocument.setMarkdown()` when opening Markdown;
  - `QTextDocument.toMarkdown()` when saving Markdown.
- Markdown conversion happens only at file boundaries.
- Normal typing, cursor movement, selection changes, toolbar synchronization, and profile switching
  must not perform Markdown conversion.
- No second source buffer, persistent AST, sidecar, database copy, synchronized Markdown string, or
  background parser.
- No new production dependency.
- Do not introduce a custom Markdown parser or serializer during the first pass.
- Do not introduce syntax validation whose purpose is to block constructs that Qt already accepts.
- Do not define an EZmd-specific canonical Markdown grammar before observing Qt's actual output.
- Exact source spelling is not promised. Qt may normalize equivalent Markdown syntax when saving.
- The Build 02 quote rail remains presentation-only. Markdown persistence should use the semantic
  state Qt produces, not the painted rail.

## Phase 1 — minimal native integration

The first Build-mode pass should make the smallest coherent change needed to exercise Qt Markdown in
the real app.

### Open

For `.md` and the existing `.markdown` alias:

1. read UTF-8 through the existing safe file path;
2. load the Markdown into a `QTextDocument` with Qt's native Markdown API;
3. present that document in the existing editor;
4. leave the opened document clean and without parser construction in user Undo history.

Keep existing safe-open behavior: a read/conversion failure must not destroy the document the user
already has open.

Do not add custom syntax inspection before `setMarkdown()` in Phase 1.

### Save

For Markdown documents:

1. obtain Markdown with Qt's native `toMarkdown()`;
2. write it using the existing safe UTF-8 file path;
3. mark the document clean only after a successful write.

Serialization must not alter the user's document, cursor, selection, semantic formatting, or undo
history.

Do not post-process Qt Markdown output in Phase 1 unless a tiny mechanical step is already required
by the existing file-writing contract, such as newline normalization.

### Plain text

Do not redesign `.txt` behavior as part of the native Markdown experiment.

Keep plain-text files using plain-text semantics for this first pass. Any change to whether `.txt`
is import-only or remains a saveable plain-text format should be a separate owner decision after the
Qt Markdown behavior is understood.

### New documents

Do not add format-selection architecture.

Use the existing save flow. Markdown paths save through `toMarkdown()`; plain-text paths retain
plain-text behavior during this experiment.

If the current UI naturally defaults new EZmd documents to Markdown, keep that small. Otherwise,
do not widen Phase 1 merely to redesign Save As behavior.

## What Phase 1 must not contain

Do not add:

- a custom Markdown tokenizer/parser;
- custom delimiter-stack logic;
- custom Markdown escaping rules;
- a supported-syntax allowlist;
- an unsupported-syntax denylist;
- custom canonical list numbering;
- custom heading/list/quote source ordering;
- custom handling for links, images, code, tables, nested structures, or other Markdown constructs
  merely because earlier drafts excluded them;
- a compatibility/source mode;
- a second document model;
- a Markdown preview;
- live source synchronization;
- background parsing;
- new dependencies.

If the implementation begins growing beyond straightforward Qt open/save integration, stop before
adding the extra machinery.

## Tests for the first pass

Automated tests should protect the integration, not attempt to specify Markdown itself.

Prove at least:

- a basic Markdown file opens into formatted `QTextDocument` state using the native path;
- a formatted document saves as Markdown rather than plain text;
- basic save -> reopen preserves representative formatting;
- opening Markdown leaves the document clean;
- open construction does not populate user Undo history;
- Save does not mutate the cursor/selection or formatting;
- failed read/write keeps existing Build 01 data-safety behavior;
- normal typing/cursor/toolbar/profile operations do not invoke Markdown conversion;
- existing Build 01/02 tests remain green.

Do not add exhaustive tests that merely duplicate Qt's Markdown test suite.

## Owner behavior survey

After the minimal native integration works, manually exercise representative Markdown and record
what actually happens. This survey is observational; it is not a prewritten support matrix.

Try at least:

- H1–H6;
- bold and italic;
- strikethrough;
- bullets and numbered lists;
- blockquotes;
- nested lists and nested blockquotes;
- links and autolinks;
- images;
- inline code and fenced code blocks;
- horizontal rules;
- tables;
- task-list-like Markdown;
- mixed/nested formatting;
- Unicode;
- blank paragraphs and empty documents;
- literal Markdown-looking punctuation;
- Markdown produced by a few ordinary external editors.

For each interesting case, answer:

1. Does Qt parse it?
2. How does it appear in the visual editor?
3. Can the user edit it sensibly?
4. What does `toMarkdown()` emit?
5. Does save -> reopen preserve the important meaning?

Do not write compatibility code during this survey.

## Decision after the survey

After owner review, classify any observed issue into one of three buckets:

1. **Works natively** — keep it. No EZmd code.
2. **Harmless normalization** — document Qt's behavior and keep it.
3. **Real fidelity/usability problem** — decide whether the smallest targeted fix belongs in Build
   03 or should be deferred.

A targeted fix requires a reproducible failing example and a regression test.

The burden of proof is on adding code, not on accepting Qt-native behavior.

## Files/roots allowed in Phase 1

Expected production changes should stay very small, primarily:

- `src/ezmd/ui/main_window.py`;
- possibly one tiny focused file-boundary helper only if it clearly improves readability;
- `tests/**`;
- this Build 03 document for factual status notes.

`src/ezmd/core/files.py` should remain unchanged unless the existing safe read/write boundary
actually lacks something required by native Markdown persistence.

Do not add `src/ezmd/core/markdown.py` merely to wrap one or two Qt calls.

If implementation requires a new production module, explain the responsibility before creating it.

## Performance constraints

- Markdown parsing occurs only on Open.
- Markdown serialization occurs only on Save.
- No normal keystroke should trigger either operation.
- No polling, file watcher, background worker, or continuously synchronized source representation.
- Keep the common writing path the same scale as Build 02.

## Data-safety constraints

The simplicity reset does not remove basic file safety:

- failed reads must not destroy current user work;
- failed writes must not mark unsaved work clean;
- opening a document should not leave parser operations in Undo;
- saving should not mutate the live document merely to serialize it;
- tests use disposable files only.

Do not add speculative loss-prevention machinery before a real native-Qt loss case is demonstrated.

## Cross-platform constraints

Linux, macOS, and Windows remain first-class targets.

Use the same Qt Markdown path on all platforms. Do not fork Markdown behavior by OS unless the
three-platform matrix demonstrates an actual difference.

## Definition of done for Phase 1

- [x] Build 02 is complete.
- [ ] Minimal Qt-native Markdown Open is implemented.
- [ ] Minimal Qt-native Markdown Save is implemented.
- [ ] No custom parser/serializer/validator was added.
- [ ] Existing Build 01/02 behavior remains green.
- [ ] Focused integration tests pass.
- [ ] `uv run --locked python bin/check.py` passes.
- [ ] Owner performs the native Markdown behavior survey.
- [ ] Any observed gaps are written down before additional Markdown code is proposed.
- [ ] Linux/macOS/Windows CI passes.

## OpenCode assignment

For the next implementation pass, use Build mode.

Implement only Phase 1 above: wire the existing file Open/Save boundary to Qt's native
`QTextDocument.setMarkdown()` and `toMarkdown()` in the smallest readable way.

Do not build a Markdown abstraction layer. Do not preemptively solve unsupported syntax. Do not add
feature-specific Markdown logic.

When complete, report:

- exact production files changed;
- approximate production-line impact;
- which Qt Markdown calls are used and where;
- focused tests added/changed;
- full gate result;
- a short list of behavior that still requires owner observation.

Then stop. Do not add compatibility fixes until the owner has tested native behavior.
