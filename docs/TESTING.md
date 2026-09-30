# Testing Philosophy

## Why tests exist

Tests are executable promises about behavior. They are not a score that proves AI-generated code
is automatically correct.

The coding agent writes tests as part of each implementation build, but the **build contract**
defines the behavior those tests must prove. Tests must not quietly redefine the product.

## Test names should explain behavior

Prefer names such as:

- `test_save_writes_the_current_document_to_the_selected_file`
- `test_canceling_new_keeps_unsaved_text`
- `test_switching_visual_profile_keeps_document_text_and_cursor`
- `test_search_never_changes_markdown_files`

## Test layers

### Unit tests

Small rules that can be checked without launching the full application.

### Integration tests

Use real temporary files, SQLite databases, encryption operations, and component boundaries when
practical. Do not mock away the behavior the test is supposed to prove.

Tests that touch user-like data must use pytest temporary directories or similarly disposable test
state. Automated tests must never touch the owner's real notes, configuration, cache, keys, or
history.

### UI tests

UI testing is a deliberate strength of this project, not a last resort.

Use `pytest-qt` to exercise real Qt Widgets for behavior that a user experiences through the UI:
editing, actions, menus/toolbars, keyboard behavior, dialogs/boundaries, focus, and profile
switching.

Do not make UI tests pixel-perfect or dependent on window-manager decorations. Test behavior and
important state, not exact raster output.

Keep business/document rules out of widgets when they can be tested directly, but do not avoid
real UI interaction tests merely because a lower-level test also exists.

### Architecture tests

A small set of checks may enforce non-negotiable boundaries that an automated coding agent could
accidentally violate. Appropriate examples include preventing Qt WebEngine/QML from entering the
primary UI architecture or preventing lower-level document logic from importing visual modules.

Do not turn this into general source-code policing.

### Smoke tests

Keep at least one very cheap test that imports or safely initializes the real application path.
Unit tests can all pass while startup is broken.

### Performance checks

Small repeatable benchmarks for startup-sensitive or search-sensitive operations. They should
catch obvious regressions without depending on unrealistically precise wall-clock timing.

## Required testing workflow

For a new feature:

1. Define behavior and acceptance promises in the build document first.
2. In Plan mode, map each promise to an appropriate test layer before implementation.
3. Implement the smallest code that satisfies those promises.
4. Write the tests as part of that implementation.
5. Run focused checks while working.
6. Run `uv run --locked python bin/check.py` before declaring the slice complete.
7. Add regression tests for real bugs as they are discovered; when practical, demonstrate that the
   test fails before the bug fix and passes after it.

## Cross-platform tests

Filesystem tests should include at least one path containing spaces and non-ASCII characters when
path handling is relevant.

Do not assert path strings using one platform's separator. Do not assume case-sensitive
filesystems. Do not use real home/config directories.

Qt CI tests run offscreen on Linux, macOS, and Windows.

## Coverage

Coverage is a map, not a target score. Use it to find important untested paths, especially
user-data loss risks, parsers/converters, state changes, error handling, search/index boundaries,
and encryption behavior.

Do not write low-value tests merely to increase a percentage.
