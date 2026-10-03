# Code style

EZmd code should teach as well as work.

## Readability

- Prefer straightforward Python and Qt APIs over clever abstractions.
- Use descriptive names. Avoid vague buckets such as `utils`, `helpers`, `manager`, `common`,
  or `misc` unless the responsibility is genuinely that broad.
- One module should answer one clear question.
- Keep functions focused. Split code when a name can describe the smaller responsibility better.
- Do not create a shared abstraction until at least two real needs justify it.
- Prefer explicit state changes over hidden side effects.

## Explanations

- Every production module gets a short module docstring describing its responsibility.
- Non-trivial production classes and functions should have a short docstring when the purpose,
  contract, or failure behavior is not obvious from the name.
- Comments explain **why**, invariants, Qt quirks, or safety constraints. Do not narrate obvious
  syntax.
- If code depends on surprising framework behavior, put the explanation next to that code.

## Qt

- Prefer native Qt document/editing behavior when it already matches the product requirement.
- Keep document semantics separate from paint-only presentation.
- Use Qt standard shortcuts when available.
- Avoid work on every keystroke unless the behavior genuinely requires it.

## Quality

- Keep strict BasedPyright clean.
- Keep Ruff formatting/lint clean.
- Do not suppress type or lint errors without a concrete explanation.
- Do not add dependencies without explicit approval.
- A coding agent should be able to explain every production file it changed and why.
