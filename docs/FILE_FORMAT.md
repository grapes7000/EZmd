# File Format

## Durable format

Plain Markdown is the default durable document format.

## User-facing rule

A user should not need to know Markdown to use EZmd.

## Build 01 interim behavior

Build 01 is deliberately pre-round-trip: it loads UTF-8 text into the native `QTextEdit` and
writes the editor's plain text back to disk using UTF-8 with LF (`\n`) line endings.

It does not parse Markdown syntax into rich formatting yet. That temporary behavior exists only to
prove safe file/window interactions before the rich document ↔ Markdown contract is introduced.

## Build 02 interim behavior

Build 02 adds an in-memory controlled rich-text vocabulary:

- Paragraph;
- H1/H2/H3;
- Bold;
- Italic;
- Strikethrough;
- bulleted list;
- numbered list;
- blockquote.

This is still a pre-round-trip development slice. Open continues to load plain UTF-8 text and Save
continues to write only the editor's plain textual content through the established safe Build 01
file path.

Build 02 formatting therefore does **not** survive close/reopen yet. Do not write Qt HTML, RTF,
opaque metadata/sidecars, or an invented partial Markdown serializer to preserve it early. Build
03 owns durable rich document ↔ Markdown conversion.

## Supported Markdown subset

Finalized during Build 03.

The controlled subset should remain intentionally small and focused on ordinary writing. The Build
02 formatting vocabulary is the starting point that Build 03 must evaluate for deliberate
round-trip support:

- Paragraphs.
- H1/H2/H3 headings.
- Bold.
- Italic.
- Strikethrough.
- Bulleted lists.
- Numbered lists.
- Blockquotes.

Links and images are desired later but are not part of Build 02's initial formatting vocabulary.
Their exact document and persistence behavior must be explicitly added by a reviewed build
contract rather than appearing incidentally.

Other formatting is supported only when explicitly justified.

## Round-trip requirement

Build 03 must define exactly what formatting the app promises to preserve when opening, editing,
and saving.

Unsupported Markdown behavior must be explicit rather than accidental.

Canonical Markdown normalization is acceptable when intentional and tested; exact original marker
choices/blank-line style are not automatically guaranteed.

## Wiki links

Planned syntax: `[[Note Name]]`.

Exact escaping, filename mapping, aliases, and rename behavior are deferred to Build 07.
