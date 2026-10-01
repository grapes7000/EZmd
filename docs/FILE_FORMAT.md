# File Format

## Durable format

Plain Markdown is the default durable document format.

## User-facing rule

A user should not need to know Markdown to use EZmd.

The normal experience is visual editing in the native document surface. Markdown is the portable on-disk representation underneath that experience.

## Builds 01–02 transition

Build 01 proves safe UTF-8 text file/window behavior.

Build 02 adds the controlled in-memory rich-text vocabulary:

- Paragraph;
- H1/H2/H3;
- Bold;
- Italic;
- Strikethrough;
- bulleted list;
- numbered list;
- blockquote.

Build 02 deliberately does not serialize that formatting. Build 03 is the first durable rich-document ↔ Markdown slice.

## Build 03 supported Markdown subset

Build 03's durable semantic vocabulary is exactly:

- Paragraphs.
- H1/H2/H3 headings.
- Bold.
- Italic.
- Strikethrough.
- Top-level bulleted lists.
- Top-level decimal numbered lists.
- One level of blockquote.
- Supported combinations of the above.

Links and images remain desired later features, but they are not Build 03 document semantics.

Other syntax is not supported merely because another Markdown implementation happens to understand it.

## Canonical output

EZmd saves a small predictable Markdown dialect.

### Headings

```markdown
# H1
## H2
### H3
```

Only H1–H3 are part of the controlled vocabulary.

### Inline formatting

```markdown
**bold**
*italic*
~~strikethrough~~
```

Combined inline formats are serialized deterministically and must reopen to the same semantic formatting.

Exact delimiter nesting for overlapping runs must be stable and tested. The semantic round-trip is the contract; preservation of the user's original delimiter spelling is not.

### Bulleted lists

```markdown
- Item one
- Item two
```

Only top-level bullets are supported.

### Numbered lists

```markdown
1. Item one
2. Item two
3. Item three
```

Any supported imported decimal markers may be normalized. EZmd canonical output begins a contiguous numbered list at `1.` and emits a normal increasing decimal sequence.

Custom start values and alternate numbering schemes are not part of Build 03.

### Blockquotes

```markdown
> Quoted paragraph
```

Only one quote level is supported.

Supported quoted block combinations may serialize as:

```markdown
> ## Quoted heading

> - Quoted list item
```

### Paragraphs and blank lines

Ordinary paragraphs use normal Markdown paragraph separation.

Soft-wrapped source layout is not preserved byte-for-byte. EZmd may normalize a visual paragraph to one logical source paragraph.

Intentional empty/blank paragraphs in the visual document must survive save/reopen.

An empty EZmd document is valid and serializes as an empty Markdown file.

## Escaping

EZmd escapes literal source characters/sequences when needed so ordinary text does not become supported formatting merely because the document was saved and reopened.

The Build 03 escaping contract deliberately covers only what its grammar needs, including:

- backslash;
- emphasis/strikethrough delimiters;
- block-leading heading markers;
- block-leading bullet markers;
- block-leading decimal-list markers;
- block-leading quote markers.

Unmatched supported delimiters are literal text.

Escaping must be deterministic enough that canonical save -> open -> save is stable.

## Open behavior

### `.md`

A `.md` file is parsed as the controlled EZmd Markdown subset.

Supported syntax becomes semantic formatting in the existing `QTextDocument`.

Opening may normalize source spelling later when the document is saved. EZmd does not promise:

- exact original delimiter choice;
- exact original list numbering text;
- exact original soft wrapping;
- exact original blank-line style;
- byte-for-byte identity.

It does promise supported visible text and supported formatting survive semantic round-trip.

### `.txt`

A `.txt` file is an import source, not a durable EZmd document mode.

- It is read as UTF-8 plain text.
- Markdown-looking characters are not parsed.
- The `.txt` path is not retained as the active overwrite target.
- The imported document is considered in need of an EZmd save.
- The natural first-save default is the source stem with `.md`.
- The original `.txt` must remain unchanged.

### Empty content

Empty `.md` and `.txt` content is valid.

"Nothing in the file" is not an error condition and does not require special syntax.

## Save behavior

EZmd's durable save format in Build 03 is `.md`.

- Existing `.md` documents save back to their Markdown path.
- New documents save as Markdown.
- Imported `.txt` documents save as Markdown.
- A filename with no suffix gains `.md`.
- EZmd must not silently establish `.txt` as a second durable rich-document format.

UTF-8 is explicit.

Canonical durable line endings are LF (`\n`) on Linux, macOS, and Windows.

The existing safe write/failure behavior remains mandatory: failed serialization/write must not discard user work or falsely mark the document clean.

## Round-trip promise

For the supported document vocabulary:

```text
QTextDocument semantic state
        ↓ serialize
canonical EZmd Markdown
        ↓ parse
QTextDocument semantic state
```

must reproduce the same supported visible text and semantic formatting.

Also:

```text
canonical save
→ open
→ canonical save
```

must be stable.

The original source bytes are not the thing being round-tripped. The supported document meaning is.

## Unsupported Markdown

Build 03 is not full CommonMark/GFM.

Unsupported constructs include, among others:

- H4–H6;
- links/autolinks;
- images;
- inline code;
- fenced/indented code blocks;
- task lists;
- tables;
- horizontal rules;
- YAML/front matter;
- HTML;
- footnotes;
- definition lists;
- nested lists;
- nested blockquotes;
- extension-specific syntax.

Unsupported constructs are not converted into new rich-editor semantics.

Their text/punctuation must not be silently deleted simply because EZmd does not understand the construct. They may appear as ordinary visible text.

Build 03 does not promise preservation of the original semantics of arbitrary external Markdown outside the supported subset.

If unsupported source contains a pattern that independently belongs to the supported grammar, only the supported portion is guaranteed semantically.

This boundary is intentional. A later reviewed build may promote a syntax into the controlled document model.

## No hidden persistence format

Build 03 must not require:

- Qt HTML;
- RTF;
- opaque metadata;
- sidecar files;
- a database copy;
- a synchronized Markdown source buffer;
- a cache that is required for fidelity.

Markdown plus the current in-memory `QTextDocument` is enough.

## Wiki links

Planned syntax: `[[Note Name]]`.

Exact escaping, filename mapping, aliases, rename behavior, and editor semantics remain deferred to Build 07.
