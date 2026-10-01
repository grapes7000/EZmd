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

## Settled decisions for this build

List product/architecture decisions that Plan mode must not reopen.

## OpenCode Plan-mode assignment

Plan only how to turn this contract into clean implementation/tests. Require:

- files/responsibilities;
- data/control flow;
- API verification needs;
- acceptance-promise → test mapping;
- cross-platform considerations;
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

TODO

## Performance constraints

TODO

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
- [ ] Focused checks passed during implementation.
- [ ] `uv run --locked python bin/check.py` passes.
- [ ] Linux/macOS/Windows CI passes where relevant.
- [ ] No later feature was implemented early.
- [ ] No unauthorized dependency was added.
- [ ] No unrelated files changed.
- [ ] Documentation matches implemented behavior.
- [ ] Complexity review completed.

## Owner review questions

TODO
