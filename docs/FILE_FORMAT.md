# File Format

## Durable format

Plain Markdown is EZmd's primary durable document format.

EZmd uses Qt's native Markdown support as the default persistence boundary. The project does not
define a parallel Markdown language unless a concrete Qt limitation proves that a small targeted
adapter is necessary.

## User-facing rule

A user should not need to know Markdown to use EZmd.

The normal experience is visual editing in the native document surface. Markdown is the portable
on-disk representation underneath that experience.

The editor remains a `QTextEdit` / `QTextDocument`, not a source editor with a rendered preview.

## Native-first persistence rule

For Markdown documents, the intended boundary is:

```text
Markdown text
    ↓
QTextDocument.setMarkdown(...)
    ↓
visual editing in the existing QTextDocument
    ↓
QTextDocument.toMarkdown(...)
    ↓
Markdown text
```

Qt-native support is accepted by default.

EZmd should not add code merely to reject, reinterpret, or reimplement Markdown constructs that Qt
can already round-trip safely through the document model.

Additional Markdown-specific code requires a demonstrated reason, such as:

- save loses meaningful information;
- the visual document cannot represent the construct safely;
- editing corrupts or materially changes the construct;
- behavior differs materially across supported platforms;
- the behavior conflicts with an explicit product decision.

Until such a case is demonstrated, prefer Qt's behavior.

## Source normalization

EZmd does not promise byte-for-byte source preservation.

Qt may normalize Markdown when a document is opened and saved, including equivalent delimiter
styles, whitespace, list-marker forms, or other source spelling.

That normalization is acceptable when the document's important visible meaning survives.

Do not create an EZmd-specific canonical Markdown dialect simply to make output differ from Qt's
native output.

## Feature support

There is no hand-maintained Markdown allowlist for Build 03.

A construct that Qt can parse, represent, edit, and serialize usefully is not considered
unsupported merely because EZmd lacks a dedicated toolbar button for it.

Likewise, the absence of a toolbar control does not justify adding validation code that blocks the
construct.

The Build 02 toolbar remains intentionally small. Markdown files may contain semantics beyond the
controls currently exposed by that toolbar if Qt preserves them safely.

Support decisions should follow observed round-trip behavior rather than a prewritten subset.

## Build 02 formatting

Build 02 provides familiar visual controls for:

- Paragraph;
- H1/H2/H3;
- Bold;
- Italic;
- Strikethrough;
- bulleted list;
- numbered list;
- blockquote.

These remain important first-party editing behaviors.

Build 03 should make these durable through the native Markdown boundary, but their existence does
not define the maximum Markdown vocabulary that may be opened.

The blockquote hairline is presentation-only. Persistence comes from the semantic
`QTextDocument` state, never from the painted rail.

## Markdown open behavior

For `.md` and the existing `.markdown` alias:

- read UTF-8 through the established safe file path;
- use Qt's native Markdown parser;
- show the resulting document directly in the existing visual editor;
- leave the opened document clean;
- do not leave parse construction in user Undo history.

Do not pre-scan Markdown to block syntax that Qt already supports.

If a real input is later proven to suffer destructive native round-trip behavior, document the
specific case and decide on the smallest targeted response.

## Markdown save behavior

For Markdown documents:

- serialize the current `QTextDocument` with Qt's native Markdown serializer;
- write through the established safe UTF-8 path;
- mark the document clean only after a successful write;
- do not mutate the live document merely to produce Markdown;
- do not serialize on every edit.

The exact Markdown spelling emitted by Qt is not itself a product contract.

## Plain text

Plain-text files remain plain text.

The first Qt-native Build 03 pass does not redesign `.txt` behavior. Markdown-looking punctuation
inside a plain-text file remains ordinary characters because the file is loaded as plain text.

Whether `.txt` should later become import-only is a separate product decision and should not be
mixed into the Markdown capability experiment.

## Empty documents and Unicode

Empty files are valid.

Markdown and plain-text file I/O use UTF-8.

Paths containing spaces and non-ASCII characters remain supported through the existing file layer.

## File safety

Existing safe file behavior remains mandatory:

- failed reads do not destroy the current document;
- failed writes do not falsely mark user work clean;
- serialization does not alter cursor/selection or document formatting;
- opening does not populate user Undo with parser construction steps.

These are file-boundary guarantees, not reasons to build a custom Markdown engine.

## No hidden persistence format

Markdown persistence must not require:

- Qt HTML;
- RTF;
- opaque metadata;
- sidecar files;
- a database copy;
- a synchronized source buffer;
- a persistent AST;
- a cache required for fidelity.

The live `QTextDocument` plus the Markdown file is the model.

## Compatibility policy

When a native Markdown behavior is surprising:

1. reproduce it with a small disposable example;
2. determine whether meaning is actually lost or merely normalized;
3. test it on the supported Qt/platform matrix when relevant;
4. add EZmd-specific code only if the problem is real and the targeted fix is simpler than living
   with or documenting Qt's behavior.

Do not add general parsing infrastructure for a local edge case.

## Wiki links

Planned EZmd-specific syntax remains `[[Note Name]]`.

Exact parsing, escaping, filename mapping, aliases, rename behavior, and editor semantics are
deferred to Build 07. That future feature may require targeted handling because it is not ordinary
Markdown syntax.
