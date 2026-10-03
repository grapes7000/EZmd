# Product

EZmd is a native desktop writing and notes application.

## Priorities

1. **Fast.** Typing, cursor movement, formatting, opening normal documents, and navigation should
   feel immediate.
2. **Simple.** The interface should behave like a familiar desktop writing tool rather than expose
   implementation details.
3. **Private.** Normal writing should not require a network service.
4. **Portable.** User documents should remain understandable outside EZmd whenever practical.
5. **Understandable code.** The application should stay small enough that the owner can learn from,
   review, and reason about it.

## Current product shape

- One native desktop window.
- One direct visual editor.
- Familiar formatting controls.
- Plain files on disk today.
- No source/preview split.
- No browser engine.
- No plugin framework.
- No hidden database required to recover documents.

## Not locked yet

The durable rich-document file format is **not currently a settled product decision**. Markdown is a
strong candidate because it is portable and human-readable, but the project will not force the
application around Markdown if real round-trip behavior makes that a poor fit.

Future search, linking, sidebars, encryption, and semantic features are ideas, not current build
contracts.
