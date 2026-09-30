# 001 — Native Qt UI

## Status

Accepted.

## Context

EZmd must be lightweight at runtime, responsive during typing, cross-platform, and understandable
without a browser-based editor stack.

## Decision

Use PySide6 / Qt 6 for the native desktop UI.

Qt is the only GUI toolkit in the initial architecture. Qt WebEngine is excluded from the core
writing experience.

## Why

- Qt provides mature native desktop widgets, text editing, dialogs, shortcuts, file APIs, and
  cross-platform behavior from one Python-facing toolkit.
- The heavy UI work is implemented in Qt/C++; Python coordinates application behavior.
- The application can remain a normal local desktop process without a browser runtime or daemon.
- PySide6 supports the project's Linux/macOS/Windows goal.

## Alternatives considered

- Browser/Electron-style editor: rejected because it adds a browser runtime and conflicts with the
  lightweight/native goal.
- Another Python GUI toolkit: no demonstrated advantage that justifies a second ecosystem.
- QML/Qt Quick: still Qt, but not selected for the primary UI; see decision 006.

## Consequences

- PySide6 is a core runtime dependency.
- UI tests must account for Qt lifecycle/event behavior.
- Platform CI must exercise Qt on Linux, macOS, and Windows.
