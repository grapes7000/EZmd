# Architecture

## Status

Accepted baseline. Change architectural direction only through an explicit decision record.

## Core idea

The application is divided into small areas with clear responsibilities.

```text
PySide6 Qt Widgets
        ↓
QTextEdit / QTextDocument
        ↓
Document operations
        ↓
Markdown files on disk

Optional derived systems:
Markdown files → search index
Markdown files → wiki-link graph
Markdown files → optional connection suggestions
```

## Primary UI architecture

The primary UI uses PySide6 **Qt Widgets**. QML/Qt Quick is not part of the initial architecture.
Qt WebEngine is not part of the core editor.

The central editable document should remain close to `QTextEdit`/`QTextDocument`. Later formatting
and Markdown serialization should work with that native document model rather than maintaining a
second editor or browser preview as the real state.

## Source of truth

Markdown files are user data and remain authoritative.

While a document is open, its Qt document is the editable in-memory state. Saving serializes the
supported document state back to Markdown. Derived databases/caches must never silently become
the only copy of user content.

Any database used for search, graph acceleration, previews, recent-file metadata, or other
derived information must be safe to delete and rebuild.

## Planned areas

### `core/`

Rules and operations central to documents and application behavior. Keep this independent from
visual styling and later feature implementations wherever practical.

### `ui/`

Qt Widgets and visual interaction. UI code should compose controls and invoke document operations;
it should not quietly become the owner of storage rules.

Visual measurements belong in the small semantic visual-profile system described in
`docs/UI_SYSTEM.md`.

### `features/`

Optional/later capabilities such as search, wiki links, graph view, and encryption. A feature
should have a narrow public boundary with core behavior.

## Dependency direction

Higher-level features may call stable core operations.

Core document code must not depend on later features such as graph view, search suggestions, or
semantic analysis.

UI styling must not own document behavior. Document behavior must not know whether the active
visual profile is Lab, QTemp, or Focus.

## Expensive work

Normal typing is sacred. Full-vault scanning, indexing, graph layout, encryption of unrelated
files, and semantic analysis must never run synchronously on every keystroke.

The Qt UI thread must stay free of avoidable expensive work.

## Cross-platform boundary

Linux, macOS, and Windows are first-class platform families. Portable Qt/standard-library APIs are
preferred over OS-specific branches. See `docs/PLATFORM_SUPPORT.md`.

## Deliberately absent architecture

Do not introduce without a later accepted decision:

- QML/Qt Quick primary UI;
- Qt WebEngine/editor browser stack;
- plugin discovery/framework;
- dependency-injection container;
- general event bus;
- background daemon/service;
- network service requirement;
- SQLite as the primary document store.

## Future architecture questions

These remain intentionally deferred until the build that needs them:

- exact controlled formatting subset for Markdown round-trip;
- autosave/recovery behavior and its interaction with later encryption;
- exact wiki-link parsing boundary;
- how optional semantic features remain isolated if they are ever added.
