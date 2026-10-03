# Testing

Tests are executable promises about behavior.

## What to test

- User-visible editing behavior.
- File safety and failure behavior.
- Important Qt state such as selection, cursor, modified state, and Undo/Redo when relevant.
- Cross-feature regressions that have actually occurred.
- Architectural boundaries only when they are true non-negotiables.

Prefer real Qt widgets with `pytest-qt` and real disposable files with `tmp_path`.

Do not write tests merely to copy Qt's own implementation or to lock in private helper structure.

## Full health gate

```bash
uv run --locked python bin/check.py
```

The gate checks:

- whitespace errors;
- obvious secret-bearing filenames;
- Ruff lint and formatting;
- strict BasedPyright;
- pytest with coverage;
- package import smoke test.

GitHub Actions runs the same gate on Linux, macOS, and Windows with Qt offscreen.

## Manual acceptance

Automated tests are not owner acceptance.

Before a build is called complete:

1. launch the real application;
2. use the new feature as a user would;
3. check the important failure/undo/save paths;
4. compare behavior with the build contract;
5. record any surprising behavior before adding more code.

A test suite passing does not by itself prove the UX is acceptable.
