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

## Supported Markdown subset

Defined during Build 03.

The subset should remain intentionally small and focused on ordinary writing:

- Paragraphs.
- Headings.
- Bold.
- Italic.
- Lists.
- Links.
- Images.
- Other formatting only when explicitly justified.

## Round-trip requirement

Build 03 must define exactly what formatting the app promises to preserve when opening, editing,
and saving.

Unsupported Markdown behavior must be explicit rather than accidental.

Canonical Markdown normalization is acceptable when intentional and tested; exact original marker
choices/blank-line style are not automatically guaranteed.

## Wiki links

Planned syntax: `[[Note Name]]`.

Exact escaping, filename mapping, aliases, and rename behavior are deferred to Build 07.
