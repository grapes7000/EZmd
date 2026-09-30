# Dependency Policy

Every dependency must justify its cost.

Before adding one, answer:

1. What problem does it solve?
2. Why is the standard library or existing dependency insufficient?
3. Does it affect startup time?
4. Does it affect memory use?
5. Does it introduce background processes or network behavior?
6. Can the feature that needs it remain optional?
7. Is the dependency actively maintained and appropriately licensed?
8. Does it work on Linux, macOS, and Windows for the project's supported Python version?

## Runtime dependencies

### PySide6

PySide6 is the native UI toolkit.

Build 01 uses a compatible range beginning at Qt for Python 6.11 and staying below Qt 7. The
lockfile records the exact development version. Do not add PyQt, QML-only UI frameworks, WebEngine,
or a second GUI toolkit.

## Planned/deferred categories

### Cryptography

Use a mature cryptography library when Build 12 reaches encryption. Never implement cryptographic
primitives in this repository.

### Search

SQLite FTS5 is the planned full-text search mechanism when Build 05 verifies it is available in
the target Python/SQLite environments.

### Fuzzy matching

A lightweight optimized library may be considered during Build 06 only if the standard-library
approach does not meet the behavior/performance contract.

### Semantic features

Must remain optional and outside the initial twelve builds.

## Selected development tooling

The baseline development group contains only:

- Ruff — linting and formatting.
- BasedPyright — type checking.
- pytest — tests.
- pytest-qt — real Qt interaction tests.
- pytest-cov — coverage visibility.

uv manages and locks these tools. `uv_build` is the packaging backend so the `src/ezmd` app is
installed cleanly into the environment and exposes an `ezmd` command.

Do not add an additional formatter, linter, type checker, test runner, task runner, UI toolkit, or
build backend unless a concrete limitation is demonstrated first.

## Security/dependency audit

A dedicated vulnerability audit is useful once runtime dependencies exist, but it should not make
the normal offline editing/check loop depend on network availability. Add it as a separately
justified CI/release check after Build 01 if it provides clear value.
