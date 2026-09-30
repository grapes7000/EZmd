# 008 — Cross-platform Desktop from the First Build

## Status

Accepted.

## Context

The owner develops on Linux but wants EZmd to remain a real desktop application for Linux, macOS,
and Windows.

## Decision

Treat Linux, macOS, and Windows as first-class platform families from Build 01 onward.

Use portable Python/Qt APIs, a Python-based quality gate, and a three-OS CI matrix. Do not defer
basic portability until release packaging.

## Why

Cross-platform assumptions are cheapest to prevent before file handling, shortcuts, tests, and
scripts become entrenched.

## Alternatives considered

- Develop Linux-only and port later: rejected because path/shell/UI assumptions would become harder
  to identify after multiple builds.
- Maintain three OS-specific codepaths: rejected unless a later feature genuinely requires an
  isolated platform adapter.

## Consequences

- Tests use temporary portable paths and avoid one-platform separator assumptions.
- CI runs Linux, macOS, and Windows.
- Application code cannot depend on Bash/PowerShell.
- Release packaging/signing remains a separate later decision.
