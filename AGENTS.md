# EZmd agent instructions

Repository documentation is authoritative. Read these before planning or editing code:

1. docs/STATUS.md
2. docs/PRODUCT.md
3. docs/ARCHITECTURE.md
4. docs/CODE_STYLE.md
5. docs/TESTING.md
6. the active build document

The active build is currently docs/builds/03-qt-markdown-persistence.md.

## Baseline rules

- Implement only an explicitly approved build or task. Do not invent the next product decision.
- Prefer the smallest readable change that solves the requested behavior.
- Keep the native Qt editor as the center of the application unless a reviewed architecture decision explicitly changes that.
- Do not add frameworks, plugin systems, managers, compatibility layers, custom Markdown parsers, custom Markdown serializers, background workers, or dependencies in anticipation of future needs.
- Production code must be understandable by a Python learner reading it carefully. Explain non-obvious Qt behavior and important invariants in comments or docstrings.
- Tests should prove user-visible behavior and safety, not mirror implementation details or duplicate Qt's own Markdown test suite.
- Do not call a build complete until automated checks pass and the owner has manually exercised the feature.
- Run the full gate before reporting implementation complete:

    uv run --locked python bin/check.py

Do not infer requirements from old branches, closed pull requests, deleted documentation, or previous Markdown experiments. The current repository docs replace them.
