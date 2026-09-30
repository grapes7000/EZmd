# 006 — Qt Widgets for the Primary UI

## Status

Accepted.

## Context

Both Qt Widgets and QML/Qt Quick can produce fast native Qt applications. EZmd's central feature,
however, is a rich editable text document that should remain easy to understand and test from
Python.

## Decision

Use PySide6 **Qt Widgets** for the primary application UI.

Do not use QML/Qt Quick as the primary UI and do not embed QML merely for decorative controls.

## Why

- `QTextEdit`/`QTextDocument` directly match the intended editable-document model.
- Widgets keep the Python → Qt → document path simple and educationally readable.
- The application does not need animation-heavy or touch-first UI behavior that would justify a
  second declarative UI layer.
- Custom visual design can be achieved through a small semantic token/profile system without QML.

## Alternatives considered

- QML/Qt Quick primary UI: technically viable and visually flexible, but adds a QML/Python bridge
  and another language/concept around the application's most important interaction.
- Hybrid Widgets + `QQuickWidget`: rejected because it adds complexity and rendering tradeoffs for
  no required Build 01 behavior.

## Consequences

- UI modules import from `PySide6.QtWidgets`, `QtGui`, and `QtCore` as needed.
- Architecture checks may guard against accidental QtQml/QtQuick/WebEngine introduction.
- Visual styling must remain centralized enough that choosing Widgets does not hard-code one look.
