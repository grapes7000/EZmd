# EZmd

EZmd is a small native desktop writing editor built with Python, PySide6, and Qt Widgets.

The product goal is simple: writing should feel immediate, familiar, private, and portable. The
implementation should stay small enough to understand.

## Current state

Production `main` contains two completed slices:

- **Build 01 — Native editor shell:** New/Open/Save, UTF-8 file I/O, unsaved-change protection,
  native desktop window, and visual profiles.
- **Build 02 — Formatting toolbar:** Paragraph/H1/H2/H3, bold, italic, strikethrough, bullets,
  numbering, blockquotes, and native Undo/Redo.

Rich formatting is currently **in-memory only**. Saving on `main` writes plain text. Build 03 has
been reset and is not implemented on `main`.

The durable rich-document format is deliberately not locked in by the current docs. Markdown remains
a candidate, but the next persistence decision will be made from observed behavior rather than old
experiments.

See `docs/STATUS.md` for the current project state.

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
- `docs/ARCHITECTURE.md` — current code structure and boundaries.
- `docs/CODE_STYLE.md` — readability rules.
- `docs/TESTING.md` — automated and manual verification.
- `docs/BUILD_PLAN.md` — completed slices and what is intentionally undecided.
- `docs/FILE_FORMAT.md` — current on-disk behavior.
