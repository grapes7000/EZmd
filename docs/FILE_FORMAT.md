# File Format

## Durable format

Plain Markdown is the default durable document format.

## User-facing rule

A user should not need to know Markdown to use EZmd.

The normal experience is visual editing in the native document surface. Markdown is the portable
on-disk representation underneath that experience.

Normal typing is literal text. Typing Markdown-looking punctuation does not itself create rich
formatting. Formatting meaning comes from the document's semantic state, normally created through
familiar editor controls. Optional Markdown typing shortcuts, if added later, must explicitly
convert recognized typing into those same document semantics rather than creating a second live
Markdown mode.

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

Build 02 deliberately does not serialize that formatting. Build 03 is the first durable
rich-document ↔ Markdown slice.

### Build 02 structural model

The visual editor's first structural model is intentionally smaller than Markdown's full grammar.

- Paragraph/H1/H2/H3 is the block style and remains independent from the structural container.
- Bold/Italic/Strikethrough may combine with supported block styles/structures.
- A block may have at most one of these top-level structural states:
  - no structure;
  - bulleted list;
  - numbered list;
  - blockquote.
- Bullet, Numbered, and Blockquote are therefore mutually exclusive in Build 02.
- Switching among Bullet/Numbered/Blockquote normalizes the block to the selected top-level
  structure; previous indentation must not leak into the new state.
- Heading level/presentation survives list/quote application and removal.
- Nested lists and nested quotes are not part of the model.

Build 03 must serialize the document model the editor can actually create rather than widening
scope merely because Markdown can express more combinations.

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
- Supported inline combinations.
- Heading + supported top-level list.
- Heading + top-level blockquote.

A list item and blockquote are not combined in the Build 02/03 document model. Markdown forms such
as `> - item` are therefore outside this build's supported structure even though Markdown itself
allows them.

Links and images remain desired later features, but they are not Build 03 document semantics.

Other syntax is not supported merely because another Markdown implementation happens to understand
it.

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

Combined inline formats are serialized deterministically and must reopen to the same semantic
formatting.

Exact delimiter nesting for overlapping runs must be stable and tested. The semantic round-trip is
the contract; preservation of the user's original delimiter spelling is not.

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

Any supported imported decimal markers may be normalized. EZmd canonical output begins a
contiguous numbered list at `1.` and emits a normal increasing decimal sequence.

Custom start values and alternate numbering schemes are not part of Build 03.

### Blockquotes

```markdown
> Quoted paragraph
```

Only one quote level is supported.

A heading may also be quoted because heading style is independent from the blockquote state:

```markdown
> ## Quoted heading
```

Quoted lists are not part of Build 03 because Build 02 treats Quote/Bullet/Numbered as mutually
exclusive structural states.

### Paragraphs and blank lines

Ordinary paragraphs use normal Markdown paragraph separation.

Soft-wrapped source layout is not preserved byte-for-byte. EZmd may normalize a visual paragraph
to one logical source paragraph.

Intentional empty/blank paragraphs in the visual document must survive save/reopen.

An empty EZmd document is valid and serializes as an empty Markdown file.

## Escaping and literal Markdown-looking text

EZmd escapes literal source characters/sequences when needed so ordinary text does not become
supported formatting merely because the document was saved and reopened.

For example, visually typing `# not a heading` into a normal Paragraph does not create H1 state.
The serializer must therefore save an escaped/canonical equivalent that reopens as the same literal
paragraph rather than accidentally changing its meaning.

The Build 03 escaping contract deliberately covers only what its grammar needs, including:

- backslash;
- emphasis/strikethrough delimiters;
- block-leading heading markers;
- block-leading bullet markers;
- block-leading decimal-list markers;
- block-leading quote markers.

Unmatched supported delimiters are literal text when they are unambiguously ordinary text rather
than an unsupported construct.

Escaping must be deterministic enough that canonical save -> open -> save is stable.

## Open behavior

### `.md`

A `.md` file is parsed as the controlled EZmd Markdown subset.

Supported syntax becomes semantic formatting in the existing `QTextDocument`.

Opening may normalize supported source spelling later when the document is saved. EZmd does not
promise:

- exact original delimiter choice;
- exact original list marker spelling;
- exact original list numbering text;
- exact original soft wrapping;
- exact original blank-line style;
- byte-for-byte identity.

It does promise supported visible text and supported formatting survive semantic round-trip.

Common equivalent spellings of the supported meanings may be accepted on input when doing so is
simple and unambiguous, then normalized to EZmd's canonical output. Examples include equivalent
bold delimiters and common top-level bullet markers. This flexibility must not widen Build 03 into
full Markdown support.

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

The existing safe write/failure behavior remains mandatory: failed serialization/write must not
discard user work or falsely mark the document clean.

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

## Unsupported Markdown: lossless or refuse

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
- quote+list combinations;
- extension-specific syntax.

The safety rule is **lossless or refuse**.

If a Markdown file contains unsupported structure that EZmd cannot safely represent in its current
visual document model, opening that file as a rich EZmd document must fail clearly and leave the
currently open document/path/modified state untouched. EZmd must not open such a file, make it look
approximately correct, and then silently destroy or reinterpret unsupported structure on Save.

This rejection is about unsupported *structure*, not ordinary literal punctuation. Literal
Markdown-looking characters that are valid plain text under the controlled grammar remain visible
text and are escaped on save when necessary.

Do not add a source/preview compatibility mode, hidden preservation sidecar, opaque metadata, or
second source buffer merely to accept unsupported Markdown. A later reviewed build may promote a
syntax into the controlled document model.

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

Exact escaping, filename mapping, aliases, rename behavior, and editor semantics remain deferred to
Build 07.
