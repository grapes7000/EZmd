# EZmd agent instructions

Repository documentation is authoritative. Read these before planning or editing code:

1. docs/STATUS.md
2. docs/PRODUCT.md
3. docs/ARCHITECTURE.md
4. docs/CODE_STYLE.md
5. docs/TESTING.md
6. docs/BUILD_PLAN.md
7. docs/UI_DIRECTION.md
8. the active build document

The active build is currently `docs/builds/04-desktop-workspace.md`.

## Baseline rules

- Implement only an explicitly approved task or Build 04 slice. Build 04 is an umbrella direction,
  not permission to implement every remaining workspace feature at once.
- Prefer the smallest readable change that solves the requested behavior.
- Keep the native Qt editor as the center of the application unless a reviewed architecture
  decision explicitly changes that.
- Keep Qt Widgets as the shipping UI stack. Do not introduce QML/Qt Quick, WebEngine, a browser
  runtime, or a second UI architecture for visual polish.
- Do not add frameworks, plugin systems, managers, compatibility layers, custom Markdown parsers,
  custom Markdown serializers, background workers, or dependencies in anticipation of future needs.
- Production code must be understandable by a Python learner reading it carefully. Explain
  non-obvious Qt behavior and important invariants in comments or docstrings.
- Tests should prove user-visible behavior and safety, not mirror implementation details or
  duplicate Qt's own Markdown test suite.
- Build 03 Markdown persistence is already merged into `main`. Its Windows CI/round-trip issue is
  known deferred debt; do not change that subsystem unless the approved task is specifically about
  it.
- Build 04 currently develops on stacked branches. Always distinguish code already on `main` from
  code present only on active development branches.
- Run the full gate before reporting an implementation slice complete:

    uv run --locked python bin/check.py

- Automated checks are not a substitute for owner visual/manual acceptance when a slice changes UI
  behavior.

Do not infer requirements from abandoned experiments. Current repository docs and the owner's
explicit task define the active contract.
