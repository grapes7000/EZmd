# 003 — No WebEngine in the Core Editor

## Status

Accepted.

## Context

The earlier `lab-workspace` preview path used a browser engine plus JavaScript renderers. That was
useful for its rich preview features but adds weight and duplicates the editor/preview state for a
product whose core goal is direct native writing.

## Decision

The core writing experience uses native Qt text rendering/editing. Do not add Qt WebEngine,
embedded browser editors, or a JavaScript editor stack to the primary application architecture.

## Why

- EZmd does not need KaTeX/Mermaid/browser-preview machinery for ordinary writing.
- One native editable document is simpler than synchronizing editor and browser preview states.
- Startup, memory use, packaging, and debugging remain easier to understand.
- This keeps the text/document path close to `QTextEdit`/`QTextDocument` for later formatting and
  Markdown serialization.

## Alternatives considered

Qt WebEngine preview, embedded web editor, Electron-style architecture.

## Consequences

Advanced browser-only rendering features are outside the core product unless a later explicit
decision demonstrates a real need and isolates the cost.
