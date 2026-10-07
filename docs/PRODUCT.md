# Product

EZmd is a native desktop writing and notes application.

## Priorities

1. Fast. Typing, cursor movement, formatting, opening normal documents, and navigation should feel
   immediate.
2. Simple. The interface should behave like a familiar desktop writing tool rather than expose
   implementation details.
3. Private. Normal writing should not require a network service.
4. Portable. User documents should remain understandable outside EZmd whenever practical.
5. Understandable code. The application should stay small enough that the owner can learn from,
   review, and reason about it.

## User experience

The normal user experience is a visual writing application.

Users should think in terms of documents, headings, bold text, lists, quotes, links, and other
familiar writing features. They should not need to understand Markdown syntax, delimiters, parsers,
or serialization.

Markdown is the storage format underneath Markdown-backed documents, but it is plumbing:

- formatting controls create visual and semantic document state;
- Markdown punctuation is not shown as the normal editing surface;
- normal menus and dialogs use product language such as "document";
- features are exposed because they make sense in the writing app, not merely because Markdown has
  syntax for them.

EZmd does not aim to be a universal Markdown compatibility editor.

## Current production shape

On `main`:

- one native desktop window;
- one direct visual editor backed by Qt's `QTextDocument`;
- familiar formatting controls;
- Qt-native Markdown persistence for `.md` and `.markdown`;
- plain-text `.txt` behavior;
- no source/preview split;
- no browser engine;
- no plugin framework;
- no hidden database required to recover documents.

## Build 04 product direction

Build 04 turns the durable editor into a complete desktop writing workspace.

The owner treats visual shell work, desktop completeness, and workspace/navigation as parts of one
ongoing build. They can be developed together in small slices rather than completed as three
separate phases.

This includes:

- a coherent compact native visual system;
- a sidebar/workspace shell;
- centered, calm writing presentation;
- ordinary desktop commands, shortcuts, dialogs, and feedback;
- document navigation, search, quick open, links, and later related-document workflows where they
  earn their complexity.

Figma and the owner's `qt-app-template` may guide visual decisions, but the shipping application
remains Qt Widgets unless a later explicit architecture decision changes that.

See `docs/UI_DIRECTION.md` and `docs/builds/04-desktop-workspace.md`.

## Non-goals and boundaries

- Do not turn EZmd into a Markdown syntax IDE.
- Do not introduce a web runtime for normal editing.
- Do not add a generic plugin framework in anticipation of future needs.
- Do not add durable page/margin metadata merely to achieve a page-like visual surface.
- Do not let workspace features create a second editable document model.
