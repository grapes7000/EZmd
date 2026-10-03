# Design Philosophy

## Product identity

EZmd is a writing application first.

It should feel approachable to someone who understands Microsoft Word or Google Docs but has
never heard of Markdown.

Markdown exists underneath the interface because it is portable, durable, human-readable, and not
tied to this application.

## Primary product priorities

Two goals outrank feature count and cleverness:

1. **EZmd should feel blazingly fast.** Normal writing, cursor movement, formatting, opening a
   document, and ordinary navigation should feel immediate. Features that make common editing feel
   sluggish are not acceptable merely because they are powerful.
2. **EZmd should feel incredibly intuitive and user-friendly.** Familiar actions should behave the
   way users reasonably expect from good desktop writing software. The interface should reveal
   complexity only when it is useful; Markdown syntax, internal document structure, and technical
   implementation details should stay out of the user's way.

When choosing between otherwise valid designs, prefer the one that makes the common writing path
faster, clearer, more predictable, and easier to discover.

A feature is not successful merely because it exists or is technically correct. It should earn its
place by improving the writing experience without compromising responsiveness, safety, or
understandability.

## The application should be

- Native.
- Fast.
- Cross-platform.
- Local-first.
- Offline-capable.
- Calm and predictable.
- Understandable from its source code.
- Safe with user documents.
- Useful without learning Markdown syntax.
- Visually distinctive without sacrificing text focus.

## The application should not become

- A browser-based editor.
- A desktop-publishing suite.
- An IDE.
- A general plugin platform.
- An AI-first product.
- A clone of every Obsidian feature.
- A clone of another editor's visual identity.
- A collection of abstractions built for hypothetical future needs.

## User experience principle

The user edits the final-looking document directly.

Formatting is applied through familiar controls such as a paragraph-style dropdown, bold, italic,
lists, links, and images.

Markdown-style shortcuts may be accepted as conveniences, but visible Markdown syntax is never
required.

Common actions should be discoverable without documentation, and keyboard shortcuts should follow
established desktop conventions where practical. Error states should explain what happened in
plain language and preserve user work.

## Visual principle

The writing surface gets the space and attention. Navigation, actions, status, and supporting
controls stay relatively small and toward the edges of the window.

Hairline separation, restrained rounding, and low-chrome controls are preferred over heavy cards,
large pills, or decorative shadows. Exact geometry is intentionally being compared through the
Lab, QTemp, and Focus profiles described in `docs/UI_SYSTEM.md`.

Visual values are semantic. A button should not carry arbitrary spacing/radius numbers merely
because one screen happened to look right. The UI should be restylable by changing profile tokens,
not by hunting through unrelated widget code.

## Simplicity principle

If two implementations satisfy the same requirements, prefer the one with:

1. Fewer moving parts.
2. Fewer dependencies.
3. Less background work.
4. More obvious data flow.
5. Easier tests.
6. Easier explanation to a new reader.

Simplicity is valuable partly because it protects the two primary product priorities: fewer moving
parts make it easier to keep the editor fast, predictable, and understandable to users and
maintainers.
