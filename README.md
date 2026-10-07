# EZmd

EZmd is a small native desktop writing editor built with Python, PySide6, and Qt Widgets.

The product goal is simple: writing should feel immediate, familiar, private, and portable. The
implementation should stay small enough to understand.

## Current state

Production `main` contains the first three implementation baselines:

- **Build 01 — Native editor shell:** New/Open/Save, UTF-8 file I/O, unsaved-change protection,
  native desktop window, and visual profiles.
- **Build 02 — Formatting toolbar:** Paragraph/H1/H2/H3, bold, italic, strikethrough, bullets,
  numbering, blockquotes, and native Undo/Redo.
- **Build 03 — Qt Markdown persistence:** `.md` and `.markdown` files use Qt's native Markdown
  conversion with a focused whitespace adapter and strict semantic Save verification. `.txt`
  remains plain text.

Build 03 is merged and is the production persistence baseline, but its final acceptance is not
closed: a Windows-only Markdown round-trip/CI issue remains intentionally deferred.

**Build 04 — Desktop workspace** is the active development direction. It treats the desktop shell
and visual system, ordinary desktop completeness, and workspace/navigation features as one
continuing product build. Work still lands as small, launchable slices rather than one large
rewrite.

Current Build 04 work is stacked off `main`: `build/04-01-design-tokens` contains the visual
tokens/themes work and PR #8's editor-pane plus collapsible-sidebar shell. Those changes are not
yet production `main`.

See `docs/STATUS.md` for the exact branch and acceptance state.

## Run

```bash
uv sync --locked
uv run --locked ezmd
```

## Check

```bash
uv run --locked python bin/check.py
```

That is the repository health gate used by CI on Linux, macOS, and Windows.

## Documentation

- `docs/STATUS.md` — what is true right now.
- `docs/PRODUCT.md` — product goals and non-goals.
- `docs/ARCHITECTURE.md` — current production code structure and boundaries.
- `docs/CODE_STYLE.md` — readability rules.
- `docs/TESTING.md` — automated and manual verification.
- `docs/BUILD_PLAN.md` — build sequence and current Build 04 scope.
- `docs/UI_DIRECTION.md` — active desktop-workspace visual and interaction direction.
- `docs/FILE_FORMAT.md` — current on-disk behavior.
- `docs/builds/04-desktop-workspace.md` — Build 04 umbrella contract and current slice state.
