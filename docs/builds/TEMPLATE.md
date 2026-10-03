# Build XX — Name

## Status

Not started.

## Minimal agent invocation

Once this contract is reviewed and marked ready, the owner should be able to invoke it with only:

```text
Plan Build XX
```

in OpenCode Plan mode, then after plan approval:

```text
Implement Build XX
```

in OpenCode Build mode. The agent must obtain requirements from `AGENTS.md`, this contract, its
referenced decisions, and the existing implementation/tests rather than requiring the owner to
restate the product specification in the prompt.

## Purpose

TODO

## Global product priorities

This build must preserve EZmd's two standing product requirements:

- normal writing and common interaction should feel **blazingly fast**;
- behavior should remain **incredibly intuitive and user-friendly**, favoring familiar desktop
  conventions and keeping Markdown/implementation complexity out of the user's way.

State any slice-specific risks to responsiveness or intuitiveness below and make them testable or
manually reviewable where practical.

## Settled decisions for this build

List product/architecture decisions that Plan mode must not reopen.

## OpenCode Plan-mode assignment

Plan only how to turn this contract into clean implementation/tests. Require:

- files/responsibilities;
- data/control flow;
- API verification needs;
- acceptance-promise → test mapping;
- cross-platform considerations;
- common-path performance/UX impact;
- complexity sanity check.

Do not re-plan product scope or later features.

## User-visible outcome

TODO

## Allowed implementation

TODO

## Files/roots allowed to change

TODO

## Approved dependencies

None unless listed here.

## Required behavior

TODO

## Explicit non-goals

TODO

## Acceptance promises and required tests

TODO

## Manual acceptance pass

Include a real-app check that the new capability feels immediate, understandable, and consistent
with familiar desktop writing behavior, in addition to the slice-specific checks.

TODO

## Performance constraints

Normal typing, cursor movement, selection, and unrelated UI work must not become slower merely
because this build exists. Keep common-path work local to the smallest relevant document/UI state.

Add slice-specific constraints here.

## Data-safety constraints

TODO

## Cross-platform constraints

Linux, macOS, and Windows remain first-class unless this build explicitly concerns a platform-only
feature.

## Expected implementation size

TODO

If implementation becomes substantially larger or more complex, stop and explain why before
continuing.

## Definition of done

- [ ] Application launches.
- [ ] Required behavior has readable tests derived from the contract.
- [ ] Normal writing/common interaction still feels immediate.
- [ ] New user-facing behavior is understandable without requiring knowledge of Markdown/internal implementation.
- [ ] Focused checks passed during implementation.
- [ ] `uv run --locked python bin/check.py` passes.
- [ ] Linux/macOS/Windows CI passes where relevant.
- [ ] No later feature was implemented early.
- [ ] No unauthorized dependency was added.
- [ ] No unrelated files changed.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.

## Owner review questions

Include at least:

- Did this build add avoidable work to normal typing/cursor/navigation paths?
- Would a normal desktop-writing user understand the new behavior without knowing Markdown or the
  implementation?

TODO
