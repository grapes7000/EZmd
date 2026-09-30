# Performance Policy

## Principle

The app should feel immediate during normal writing.

## Startup

Startup must not require:

- Network activity.
- Full-vault indexing.
- Graph layout.
- Semantic-model loading.
- WebEngine or a browser runtime.
- Background services/daemons.

## Typing

Normal typing must not synchronously trigger:

- full filesystem scans;
- full-vault searches;
- graph recomputation;
- semantic analysis;
- encryption work for unrelated files;
- expensive conversion of unrelated documents;
- global stylesheet/profile regeneration.

## Visual profiles

Applying a visual profile may do the small amount of whole-application styling work needed when the
user explicitly changes the profile. It must not be re-applied per keystroke or on unrelated
document changes.

## Saving

Saving one document should touch only that document and data directly derived from it whenever
practical.

## Background work

Future background work must be interruptible or isolated so it cannot make typing feel sluggish.
Do not add threads/workers merely because they might be useful later.

## Measurement

Specific startup, search, memory, and indexing budgets will be added after executable builds
provide a real measurable baseline. Avoid flaky tight timing assertions before then.
