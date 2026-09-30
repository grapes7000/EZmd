# UI Tests

Build 01 introduces real Qt interaction tests with `pytest-qt`.

UI tests should exercise meaningful user behavior through actual widgets/actions where practical:
editing, undo/redo, file actions, unsaved-change protection, and live visual-profile switching.
They should not merely assert implementation details or widget-tree trivia.

All file interaction must use pytest temporary directories. CI runs Qt without a visible display.
