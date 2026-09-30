# Review Checklist

Use this after every build and before merging substantial changes.

## Contract

- [ ] The active build contract was read before implementation.
- [ ] The implementation satisfies the documented behavior rather than an agent-invented variant.
- [ ] No product/architecture decision was silently reopened in implementation.

## Behavior

- [ ] The build's required user-visible behavior works.
- [ ] Existing behavior still works.
- [ ] Failure/cancel cases are explicit and understandable.
- [ ] New or changed behavior has appropriate tests derived from acceptance promises.

## Verification

- [ ] Focused checks were used while developing the change.
- [ ] `uv run --locked python bin/check.py` passes locally.
- [ ] Linux/macOS/Windows CI is green when the change is ready to merge.
- [ ] Any third-party API or behavior newly relied upon was verified rather than guessed.
- [ ] Coverage was reviewed for meaningful missing paths, not chased as a score.

## Scope

- [ ] Only intended files changed.
- [ ] No later feature was implemented early.
- [ ] No unauthorized dependency was added.
- [ ] No check, test, or type rule was weakened merely to make the build green.

## Simplicity

- [ ] Every new file has one clear responsibility.
- [ ] Every new class is clearly more appropriate than a function or simple data structure.
- [ ] No abstraction exists only for a hypothetical future feature.
- [ ] No duplicate mechanism was added for something the app already does.

## UI system

- [ ] User-facing visual values were added to semantic tokens/profiles instead of scattered
      through unrelated widget code.
- [ ] Document behavior does not depend on the active Lab/QTemp/Focus profile.
- [ ] Low-chrome controls still have visible keyboard focus/checked/disabled states.
- [ ] No QML/Qt Quick or WebEngine dependency entered the primary UI.

## Cross-platform

- [ ] Production code does not assume POSIX paths, Bash, a particular drive/root, or one path
      separator.
- [ ] Relevant file tests include safe temporary paths with spaces/non-ASCII characters.
- [ ] No platform was removed from CI to hide a compatibility failure.
- [ ] Platform-specific code exists only where portable Qt/Python APIs are insufficient.

## Performance

- [ ] Normal typing performs no new unnecessary expensive work.
- [ ] Startup performs no new unnecessary expensive work.
- [ ] Saving touches only what is needed.
- [ ] No expensive synchronous operation was accidentally added to the Qt UI thread.

## Data and security safety

- [ ] User Markdown remains authoritative unless an explicitly documented encrypted format applies.
- [ ] Derived data can be rebuilt.
- [ ] Tests/fixtures cannot touch real user notes, configuration, cache, history, or keys.
- [ ] Multi-file operations either have a safe failure strategy or are explicitly prevented from
      partial destructive changes.
- [ ] No secret/private data is logged or committed.
- [ ] No hidden network or filesystem writes were introduced.
- [ ] Broad exception handling, dynamic execution, unchecked paths/input, and insecure defaults
      were reviewed.

## Types and suppressions

- [ ] New function boundaries have useful, truthful types.
- [ ] Casts, ignores, and suppressions are narrow and justified.
- [ ] A checker warning was not hidden instead of fixing a real mismatch.

## Understanding

- [ ] The owner can explain why each new module exists.
- [ ] Important functions have obvious names.
- [ ] Comments explain reasons, constraints, or safety rules rather than syntax.
- [ ] Tests read like promises about behavior.
- [ ] The final diff is understandable and contains no unrelated cleanup.
