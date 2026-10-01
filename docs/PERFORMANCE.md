# Performance Policy

## Principle

The app should feel immediate during normal writing.

Performance is a product requirement, not a later optimization pass. If a feature design makes
ordinary typing, cursor movement, formatting, opening a typical document, or common navigation
feel noticeably sluggish, redesign the feature before accepting that cost.

Prefer simple work that is local to the active document or current interaction. Do not trade away
responsiveness for speculative convenience, background intelligence, or architectural generality.

## Startup

Startup must not require:

- Network activity.
- Full-vault indexing.
- Graph layout.
- Semantic-model loading.
- WebEngine or a browser runtime.
- Background services/daemons.

The initial window and editor should become usable as directly as practical; unrelated future
features should not sit on the startup path.

## Typing

Normal typing must not synchronously trigger:

- full filesystem scans;
- full-vault searches;
- graph recomputation;
- semantic analysis;
- encryption work for unrelated files;
- expensive conversion of unrelated documents;
- global stylesheet/profile regeneration.

Typing, selection, cursor movement, and simple formatting should operate on the smallest relevant
range/state rather than repeatedly walking the whole document when Qt already provides local
state.

## Visual profiles

Applying a visual profile may do the small amount of whole-application styling work needed when the
user explicitly changes the profile. It must not be re-applied per keystroke or on unrelated
document changes.

## Opening and saving

Opening one document should parse/read only what is needed for that document. Saving one document
should touch only that document and data directly derived from it whenever practical.

Parsing/serialization work belongs at explicit open/save boundaries unless a build contract has a
specific reason to do otherwise. Do not repeatedly serialize the whole document during ordinary
typing merely to keep a second representation synchronized.

## Background work

Future background work must be interruptible or isolated so it cannot make typing feel sluggish.
Do not add threads/workers merely because they might be useful later.

## Measurement

Specific startup, search, memory, and indexing budgets will be added after executable builds
provide a real measurable baseline. Avoid flaky tight timing assertions before then.

Use measurement when performance is uncertain instead of assuming a more elaborate architecture
will be faster. A simple implementation that is demonstrably immediate is preferable to an
unmeasured optimization framework.
