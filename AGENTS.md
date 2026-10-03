# EZmd agent instructions

Repository documentation is authoritative. Read these before planning or editing code:

1. `docs/STATUS.md`
2. `docs/PRODUCT.md`
3. `docs/ARCHITECTURE.md`
4. `docs/CODE_STYLE.md`
5. `docs/TESTING.md`
6. the active build document, if one exists

## Baseline rules

- Implement only an explicitly approved build or task. Do not invent the next product decision.
- Prefer the smallest readable change that solves the requested behavior.
- Keep the native Qt editor as the center of the application unless a reviewed architecture decision
  explicitly changes that.
- Do not add frameworks, plugin systems, managers, compatibility layers, parsers, background workers,
  or dependencies in anticipation of future needs.
- Production code must be understandable by a Python learner reading it carefully. Explain non-obvious
  Qt behavior and important invariants in comments or docstrings.
- Tests should prove user-visible behavior and safety, not mirror implementation details.
- Do not call a build complete until automated checks pass and the owner has manually exercised the
  feature.
- Run the full gate before reporting implementation complete:

```bash
uv run --locked python bin/check.py
```

The project will add more precise OpenCode workflow instructions after the next architecture
discussion. Until then, do not infer missing requirements from old branches, closed pull requests, or
deleted documentation.
