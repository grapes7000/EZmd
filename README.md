# EZmd

A fast, private native writing and notes application whose documents happen to be portable
Markdown files.

> **Markdown file format, non-Markdown user experience.**
> **The editor stays tiny. Intelligence gets layered on top.**

The user experience should feel familiar to people who know Microsoft Word or Google Docs.
Markdown is an implementation and portability detail, not a prerequisite for using the app.

## Project goals

- Native and extremely responsive.
- Cross-platform across Linux, macOS, and Windows.
- Simple enough for a beginner to read and understand the source.
- Plain Markdown files remain the durable source of truth.
- PySide6 Qt Widgets for the primary UI.
- No QML/Qt Quick in the initial UI architecture.
- No WebEngine, browser runtime, or JavaScript editor stack.
- Features are added in small, launchable vertical slices.
- Optional intelligence must never make normal writing slower.
- Every dependency and abstraction must justify its existence.
- Visual rules use semantic profiles rather than scattered pixel literals.

## Development baseline

The repository uses uv, Ruff, BasedPyright, pytest, pytest-qt, and pytest-cov.

The runtime UI dependency is PySide6/Qt 6. The project is a packaged `src/ezmd` application using
uv's build backend, so the application command is:

```text
uv run ezmd
```

The complete cross-platform quality gate is:

```text
uv run --locked python bin/check.py
```

On Linux/macOS, `./bin/check` is a convenience wrapper. On PowerShell,
`./bin/check.ps1` is the equivalent convenience wrapper. CI calls the same Python gate directly
on Linux, macOS, and Windows.

## Agent workflow

Product scope and architecture are decided in repository documents before implementation.
Coding agents are implementation engineers: they plan code structure, write the code, and write
the tests that prove the active build contract. They do not redesign the product or add later
features.

Read `AGENTS.md` before asking OpenCode/Codex or another coding agent to plan or build anything.

## Current status

Build 01 — Native Editor Shell — is complete. The app has a native Qt Widgets writing window,
safe basic UTF-8 file operations, unsaved-change protection, native undo/redo, and live semantic
visual profiles. The repository health gate passes on Linux, macOS, and Windows CI.

Build 02 — Word-like Formatting Toolbar — is the active reviewed contract and is ready for
OpenCode Plan mode. It adds the first controlled rich-text vocabulary while deliberately leaving
Markdown persistence to Build 03.

Start with:

- `docs/BUILD_PLAN.md`
- `docs/builds/02-formatting-toolbar.md`
- `docs/UI_SYSTEM.md`
- `docs/FILE_FORMAT.md`
- `docs/FUTURE_IDEAS.md` for deferred context that is explicitly **not** active-build permission
- `docs/PLATFORM_SUPPORT.md`
- `docs/HARDENING.md`
