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
uv's build backend so the eventual command can simply be:

```text
uv run ezmd
```

Before the first implementation build, generate and review the lockfile once:

```text
uv lock
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

Repository scaffold only. Build 01 is specified but no application feature code has been
implemented yet.

Start with:

- `docs/BUILD_PLAN.md`
- `docs/builds/01-native-editor-shell.md`
- `docs/UI_SYSTEM.md`
- `docs/PLATFORM_SUPPORT.md`
- `docs/HARDENING.md`
