# Build 05 — Full-text Search

## Status

Not started.

## Agent planning rule

Before this build starts, its placeholders must be replaced with a reviewed product contract. OpenCode Plan mode then plans only the implementation/code/test structure needed to satisfy that contract, following `AGENTS.md`. It must not invent adjacent features or redesign settled architecture.

## User-visible outcome

The user can search across document titles and contents and see relevant matching notes quickly.

## Concepts to understand before building

Search indexes; disposable derived data; SQLite FTS5; query results; incremental index updates.

## Allowed implementation

To be finalized immediately before this build begins.

## Files allowed to change

To be finalized immediately before this build begins.

## New dependencies

None unless this document is explicitly amended before implementation.

## Required behavior

To be specified and reviewed before implementation.

## Explicit non-goals

No fuzzy filename search, semantic search, wiki-link creation, tags, query language, or graph features.

## Acceptance tests

To be written as plain-language promises and reviewed before implementation.

## Performance constraints

Normal typing and startup must not become slower for work unrelated to this feature.

## Data-safety constraints

User documents must never be silently lost, partially rewritten, or made dependent on disposable derived data.

## Cross-platform constraints

Linux, macOS, and Windows remain first-class targets. Use portable Qt/Python behavior and test platform-relevant file/UI behavior for this slice.

## Expected implementation size

To be estimated before implementation. If the implementation becomes substantially larger or more complex, stop and explain why before continuing.

## Definition of done

- [ ] Application launches.
- [ ] Focused checks passed during implementation.
- [ ] `uv run --locked python bin/check.py` passes.
- [ ] New required tests pass.
- [ ] No unrelated files changed.
- [ ] No unauthorized dependency was added.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.

## Owner review questions

To be added before implementation so the owner knows what to inspect in the resulting code.
