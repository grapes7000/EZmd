# Build 09 — Search-and-Link Across Documents

## Status

Not started.

## Agent planning rule

Before this build starts, its placeholders must be replaced with a reviewed product contract. OpenCode Plan mode then plans only the implementation/code/test structure needed to satisfy that contract, following `AGENTS.md`. It must not invent adjacent features or redesign settled architecture.

## User-visible outcome

The user can find a term across multiple documents, preview proposed wiki-link changes, and safely apply selected changes.

## Concepts to understand before building

Multi-file edits; previews/diffs; atomicity or rollback strategy; exact matching boundaries; safe failure.

## Allowed implementation

To be finalized immediately before this build begins.

## Files allowed to change

To be finalized immediately before this build begins.

## New dependencies

None unless this document is explicitly amended before implementation.

## Required behavior

To be specified and reviewed before implementation.

## Explicit non-goals

No automatic bulk rewriting without user approval, semantic replacement, hidden background edits, or graph inference.

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
