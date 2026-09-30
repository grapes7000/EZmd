# Code Style

## Goal

Source code should be readable by the project owner even while they are still learning Python.

"Beautiful Python" in this repository means obvious responsibilities, honest types, direct data
flow, and small functions—not clever compression or architecture for its own sake.

## Principles

- Use descriptive names over abbreviations.
- Keep functions focused on one obvious job.
- Keep files focused on one obvious responsibility.
- Avoid generic dumping-ground modules such as `utils.py`, `helpers.py`, `manager.py`, `common.py`,
  or `misc.py` unless the name truly describes one narrow domain concept.
- Prefer explicit data flow over hidden global state.
- Prefer standard library/Qt features when they are clear and sufficient.
- Prefer functions and simple data structures before introducing classes.
- Use classes when identity, lifetime, Qt object behavior, or bundled state genuinely benefits
  from them.
- Let BasedPyright inference work; do not annotate every local variable just to make code look
  "typed."
- Put useful types on function boundaries and important data structures.
- Explain architectural reasons in comments/docstrings.
- Do not comment obvious syntax.

## Qt-specific readability

- Keep signal/action connections close to the controls they govern when that remains readable.
- Avoid giant `MainWindow` methods that mix UI construction, file I/O, styling, and business
  rules.
- Do not create a controller/service hierarchy just to avoid a moderately sized widget.
- Prefer Qt standard actions/shortcuts/dialogs when they match the product contract.
- Centralize visual tokens/profile values; do not scatter arbitrary pixel values through widget
  code.
- No QML/Qt Quick or WebEngine in the primary UI architecture.

## Cross-platform readability

- Prefer `pathlib.Path` for application file paths.
- Never manually split path strings on `/` or `\\`.
- Do not hide platform-specific assumptions in shell scripts when Python/Qt can express them
  portably.

## File header convention

Important modules should begin with a short module docstring explaining:

1. What this file is responsible for.
2. What it deliberately does not own.
3. Any safety/performance/platform rule a future editor must preserve.

Do not add ceremonial module docstrings to tiny files when they explain nothing useful.

## Naming examples

Prefer:

- `open_document`
- `save_document`
- `apply_visual_profile`
- `find_wiki_links`
- `rebuild_search_index`
- `documents_containing`

Avoid unnecessarily abstract names such as:

- `process`
- `handler`
- `manager`
- `service_factory`
- `engine` when it is merely one function or mapping.

## Tool-enforced rules

Ruff formats/lints. BasedPyright checks types. pytest checks behavior. Do not duplicate these jobs
with another formatter/linter/type checker/test runner.
