# AGENTS.md

## Purpose

This repository is developed in small, pre-decided build slices. A coding agent is an
**implementation engineer**, not the product designer or project architect.

The project owner and the repository documents decide what EZmd is, what each build must do,
what it must not do, and which architectural boundaries are settled. The coding agent decides
how to turn the active build contract into clear, compact, well-tested Python.

The goal is not merely working code. The goal is small, obvious, testable code that a
non-expert owner can read, explain, and defend.

## Authority and reading order

Repository documentation is authoritative. Do not replace a settled repository decision with a
personal preference, framework convention, remembered best practice, or speculative redesign.

Before planning or editing any build, read in this order:

1. `AGENTS.md`.
2. `docs/DESIGN_PHILOSOPHY.md`.
3. `docs/ARCHITECTURE.md`.
4. `docs/PLATFORM_SUPPORT.md`.
5. `docs/HARDENING.md` and `docs/TESTING.md`.
6. For UI work, `docs/UI_SYSTEM.md`.
7. The active file in `docs/builds/`.
8. Every decision record referenced by the active build.
9. Existing implementation and tests in the area being changed.

Later-build documents are context, not permission to implement later features early.

## Product priorities that apply to every build

Two product qualities are global constraints, even when an active build document does not repeat
them word-for-word:

1. **Blazingly fast interaction.** Normal writing, cursor movement, selection, ordinary formatting,
   opening a typical document, and common navigation should feel immediate. Do not accept avoidable
   work on the hot path merely to make an implementation more general or future-proof.
2. **Incredibly intuitive, user-friendly behavior.** Prefer familiar desktop-writing conventions,
   clear discoverability, predictable state changes, and plain-language errors. Do not expose
   Markdown syntax, implementation structure, or technical complexity to the user unless the
   product contract explicitly calls for it.

When several implementations satisfy the contract, prefer the one that best preserves those two
qualities while remaining safe and understandable. A technically correct feature that noticeably
slows normal writing or makes a familiar action confusing is not complete.

## Minimal build invocation

The repository is intentionally documented so the owner should not need to paste a second product
specification into the coding-agent prompt.

A short invocation is enough when the numbered build contract is marked ready, for example:

```text
Plan Build 02
```

in OpenCode Plan mode, followed after owner approval by:

```text
Implement Build 02
```

in OpenCode Build mode.

If the owner writes only `Build 02`, use the currently selected OpenCode mode to determine whether
the request is to plan or implement. Resolve the number to the unique matching file under
`docs/builds/` and treat that file as the active contract. The build contract, this file, its
referenced decisions, and the existing code/tests contain the requirements; do not ask the owner
to restate them in a long prompt.

If no unique matching build file exists, the build is not marked ready for the requested phase, an
approved implementation plan is required but missing, or the repository documents conflict in a
material way, stop and report that exact issue instead of guessing.

`docs/FUTURE_IDEAS.md` is durable context only. It is not authorization to pull deferred ideas into
an active build unless that build contract explicitly promotes them into scope.

## OpenCode Plan mode

Plan mode plans **implementation**, not the product.

A good plan answers:

- Which allowed files will probably be added or changed?
- What is the smallest code structure that can satisfy the active build contract?
- How will data and control flow through that structure?
- Which Qt/Python APIs need to be verified before relying on them?
- Which acceptance promise maps to which test or test group?
- Which tests are unit, integration, UI, smoke, or architecture tests?
- What cross-platform details need care on Linux, macOS, and Windows?
- What focused checks should be run while implementing?
- Does the expected implementation still fit the build's size/complexity budget?
- Does the plan preserve immediate common-path interaction and familiar/user-friendly behavior?

Plan mode must **not**:

- propose a different product architecture when the documented one satisfies the build;
- redesign the roadmap;
- add features for convenience or future use;
- introduce dependencies not allowed by the build;
- create a plugin framework, dependency-injection framework, service layer, registry, or other
  architecture merely because it might be useful later;
- reinterpret an acceptance promise into something easier to implement or test;
- spend time re-planning decisions already marked accepted.

If the contract is internally inconsistent, technically impossible as written, or materially
ambiguous, report the exact conflict. Do not silently choose a new product behavior.

## OpenCode Build mode

Build mode implements the approved build contract and the implementation plan.

The coding agent **owns**:

- local module/function/class decomposition;
- readable names;
- straightforward Qt signal/action wiring;
- narrow helper functions when they make behavior easier to understand;
- exact test code and fixtures needed to prove the documented promises;
- local error handling needed by the contract;
- verifying third-party APIs against the installed version or authoritative documentation;
- simplifying its own code when the first implementation is more complicated than necessary.

The coding agent **does not own**:

- product scope;
- feature prioritization;
- the application's architectural direction;
- changing source-of-truth rules;
- changing the UI technology;
- changing cross-platform support;
- adding future features;
- weakening the quality gate;
- changing visual-profile intent outside the active build.

Tests are part of the implementation. Derive them from the build's acceptance promises; do not
invent product behavior merely to create a convenient test.

## Non-negotiable rules

1. Inspect before editing. Read the active build document, relevant implementation, nearby tests,
   configuration, and referenced decisions before changing code.
2. Change only files/roots allowed by the build document unless the document is explicitly
   amended first.
3. Do not add dependencies unless the build document explicitly allows them.
4. Do not implement features scheduled for later builds.
5. Do not create abstractions for hypothetical future needs.
6. Prefer a plain function over a class when a class is not clearly necessary.
7. Prefer direct code over factories, registries, service locators, dependency-injection
   frameworks, or plugin systems.
8. Do not rewrite or "clean up" unrelated working code while implementing a feature.
9. Work in coherent small batches. Run the narrowest useful check after each batch and the full
   repository gate before completion.
10. Never weaken linting, formatting, typing, tests, or architecture checks merely to make them
    pass. Any necessary suppression must be narrow, local, and documented.
11. Do not perform expensive work on every keystroke unless the build explicitly requires it.
12. Do not add background services, daemons, telemetry, analytics, or network access.
13. User Markdown files are authoritative. Caches and indexes must be disposable.
14. The application must remain launchable after every completed build slice.
15. Tests must describe user-visible behavior or important architectural guarantees rather than
    mirror internal implementation.
16. Automated tests must use disposable state and must not touch real user notes, configuration,
    cache, history, or encryption material.
17. The application targets Linux, macOS, and Windows. Production code must not assume POSIX
    paths, Bash, one desktop environment, one path separator, or case-sensitive filesystems.
18. A passing test suite is necessary but not sufficient. Code must also remain understandable
    and appropriately small.
19. Comments should explain *why* a decision exists, not narrate obvious Python syntax.
20. Treat generated code and remembered library APIs as untrusted until verified against the
    installed version, authoritative source, or an exercising test.
21. If a requirement is materially ambiguous, stop and report the ambiguity instead of inventing
    a product decision.
22. If implementation becomes substantially larger or more complex than the build document
    anticipates, stop and explain why before continuing.
23. Do not make a familiar user interaction surprising merely because a different behavior is
    easier to code. Follow the build contract and established desktop conventions where they apply.
24. Keep common-path work local. Avoid whole-document, whole-vault, or global UI work during normal
    typing/cursor movement when a smaller operation satisfies the same behavior.

## Required workflow for every build

1. Follow the reading order above.
2. In Plan mode, produce an implementation/test/platform plan limited to the active build.
3. Inspect the existing code and tests that the slice will touch.
4. Implement only the required slice.
5. Add/update the tests required by the acceptance promises.
6. Run focused checks while working.
7. Run the cross-platform repository health gate before completion:
   `uv run --locked python bin/check.py`.
8. Review the final diff for unrelated changes, hidden I/O, unsafe error handling, type
   suppressions, platform assumptions, unnecessary abstraction, common-path performance costs,
   and confusing user-facing behavior.
9. Update documentation only when implementation changed a documented fact or the active build
   status.
10. Summarize exactly what changed, what was tested, and any remaining uncertainty.

## Complexity review before completion

Ask:

- Could this use fewer concepts?
- Could any new class be a function instead?
- Could any new module be removed?
- Was anything created only because it *might* be useful later?
- Did this duplicate an existing capability?
- Does normal typing, opening, or saving now do extra work it did not need to do before?
- Did a new abstraction make the code harder for the owner to explain?
- Is any platform-specific branch present that Qt, `pathlib`, or the standard library already
  handles portably?
- Would a normal user understand the new interaction without knowing how the code works?
- Is there a simpler interaction that is more familiar without weakening the product contract?

If yes, simplify before marking the build complete.
