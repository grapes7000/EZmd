# Tests

Tests are executable promises from the active build contract.

Structure:

- `unit/` — small pure rules;
- `integration/` — real temporary files/databases/component boundaries;
- `ui/` — meaningful Qt Widget interaction through pytest-qt;
- `smoke/` — cheap real-package/application initialization checks;
- `architecture/` — a few non-negotiable boundaries;
- `performance/` — later repeatable regression checks.

All user-like filesystem state must live under pytest temporary directories. Tests must never touch
real notes, config, cache, history, or keys.
