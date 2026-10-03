# Product

EZmd is a native desktop writing and notes application.

## Priorities

1. Fast. Typing, cursor movement, formatting, opening normal documents, and navigation should feel immediate.
2. Simple. The interface should behave like a familiar desktop writing tool rather than expose implementation details.
3. Private. Normal writing should not require a network service.
4. Portable. User documents should remain understandable outside EZmd whenever practical.
5. Understandable code. The application should stay small enough that the owner can learn from, review, and reason about it.

## User experience

The normal user experience is a visual writing application.

Users should think in terms of documents, headings, bold text, lists, quotes, links, and other familiar writing features. They should not need to understand Markdown syntax, delimiters, parsers, or serialization.

Markdown may be the storage format underneath the editor, but it is plumbing:

- formatting controls create visual and semantic document state;
- Markdown punctuation is not shown as the normal editing surface;
- normal menus and dialogs should use product language such as "document" rather than teaching users Markdown terminology;
- features are exposed because they make sense in the writing app, not merely because Markdown has syntax for them.

EZmd does not aim to be a universal Markdown compatibility editor. Features the product does not expose are not part of the promised editing experience merely because an external Markdown flavor supports them.

## Current product shape

- One native desktop window.
- One direct visual editor.
- Familiar formatting controls.
- No source/preview split.
- No browser engine.
- No plugin framework.
- No hidden database required to recover documents.

## Visual direction

EZmd should eventually feel polished, calm, and obvious rather than developer-oriented.

A future UI-design pass may use Figma to explore layouts, spacing, hierarchy, controls, empty states, sidebar/workspace patterns, and interaction flows before implementation. Figma is a design and review tool only; the shipping application remains native Qt Widgets unless a later explicit architecture decision changes that.

## Future product areas

After durable documents work, the project should focus on three broad areas:

1. Desktop completeness — the ordinary commands, shortcuts, dialogs, feedback, and small conveniences users expect from a desktop editor.
2. UI polish — a coherent visual system and interaction design, potentially explored in Figma before coding.
3. Workspace features — document navigation, sidebar behavior, search, quick open, links, and related organization features.

These are direction, not permission to implement them early.
