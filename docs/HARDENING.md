# Python Hardening

## Goal

Make mistakes easy to detect without turning development into a slow ritual. The quality system
should be as small and understandable as the application.

## Baseline toolchain

- **uv** — Python environment, dependency management, lockfile, and project command execution.
- **uv_build** — small build backend for the packaged `src/ezmd` application.
- **Ruff** — formatting and linting.
- **BasedPyright** — static type checking.
- **pytest** — behavioral and integration tests.
- **pytest-qt** — Qt Widget interaction tests.
- **pytest-cov** — coverage visibility; coverage is a map, not a score.
- **GitHub Actions** — runs the same Python health-gate logic on Linux, macOS, and Windows.

All configuration belongs in `pyproject.toml` unless a tool cannot reasonably be configured there.

## One health gate

Canonical command on every platform:

```text
uv run --locked python bin/check.py
```

Convenience launchers:

```text
./bin/check        # Linux/macOS/POSIX shell
./bin/check.ps1    # Windows PowerShell
```

The launchers contain no quality logic. `bin/check.py` is the single implementation used by
people and CI.

The gate checks:

1. whitespace errors via Git;
2. a small set of obvious secret-bearing tracked filenames;
3. Ruff lint;
4. Ruff format verification;
5. BasedPyright;
6. pytest with coverage;
7. a cheap real-package import/startup smoke check.

The gate does not modify source code.

## Focused first, broad second

During implementation, run the narrowest useful check after a coherent change. Examples:

```text
uv run ruff check src/ezmd/some_file.py
uv run basedpyright src/ezmd/some_file.py
uv run pytest tests/ui/test_some_behavior.py
```

Before a build slice is considered complete, run the full cross-platform gate locally and ensure
the GitHub Actions matrix is green.

## Never weaken checks to get green

Do not solve a failure by broadly disabling a rule, deleting a meaningful test, hiding code from
the checker, or adding a blanket ignore.

A narrow suppression is acceptable only when the underlying library/type information is genuinely
wrong or dynamic, and the reason is documented beside the suppression.

## AI-written code is untrusted until verified

Generated code must not assume that an API, import, configuration key, return type, exception, or
library behavior exists. Verify relevant third-party behavior against the installed version or an
authoritative source and run checks that exercise it.

Review AI-written changes specifically for:

- broad or swallowed exceptions;
- hidden network or filesystem writes;
- secret/private-data logging;
- insecure defaults;
- unchecked user-controlled paths or input;
- `eval` / `exec` or similar dynamic execution;
- synchronous expensive work on the Qt UI thread;
- casts, ignores, or suppressions hiding real type mismatches;
- platform-specific path/shell assumptions;
- new dependencies or architectural layers not required by the active build.

## Reproducibility

- Supported Python begins at 3.12 unless a decision record changes it.
- `.python-version` gives the preferred development interpreter.
- Runtime dependencies live in `[project].dependencies`.
- Development tools live in the `dev` dependency group.
- `uv.lock` is committed and reviewed.
- Normal checks use `--locked` so dependency drift cannot happen silently.

## CI platform matrix

Quality checks run on:

- Ubuntu;
- Windows;
- macOS.

Qt runs in offscreen mode in CI. A platform failure is a real compatibility signal; do not simply
remove that platform from the matrix to make CI green.

## Deferred tools

Do not add tools merely because they are common in mature repositories.

Potential later additions include dependency vulnerability auditing, dead-code/dependency
analysis, mutation testing, or specialized security checks. Add them only when they solve a
concrete problem without making the normal feedback loop annoying.
