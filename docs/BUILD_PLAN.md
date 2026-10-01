# Build Plan

Every numbered build is a **product contract** decided before coding begins. OpenCode Plan mode may
plan how to implement the active contract; it may not redesign the roadmap or add adjacent
features.

Every completed build must leave the application runnable and testable.

Across every slice, two global product priorities remain in force: EZmd should feel **blazingly
fast** and **incredibly intuitive/user-friendly**. A build that adds the requested capability but
makes normal writing noticeably slower or a familiar interaction confusing is not complete.

| Build | Status | Slice | Main result |
|---|---|---|---|
| 01 | Complete | Native editor shell | Cross-platform Qt Widgets editor with safe basic file actions and live visual profiles |
| 02 | Active | Formatting toolbar | Familiar Word-like formatting controls |
| 03 | Contract drafted — blocked on Build 02 acceptance | Markdown round-trip | Open/save the supported rich-document subset as predictable Markdown |
| 04 | Future | Document sidebar | Browse folders and notes |
| 05 | Future | Full-text search | Fast search across note contents |
| 06 | Future | Fuzzy Quick Open | Instant keyboard-driven note opening |
| 07 | Future | Wiki links | Link notes to other notes |
| 08 | Future | Backlinks | See which notes refer to the current note |
| 09 | Future | Search-and-link | Safely create links across multiple notes |
| 10 | Future | Explicit-link graph | Visualize real wiki-link relationships |
| 11 | Future | Connection suggestions | Find lightweight lexical/topic relationships |
| 12 | Future | Encryption at rest | Protect opted-in private storage correctly |

Optional semantic/embedding work is outside the first twelve builds.

`docs/FUTURE_IDEAS.md` records deferred product ideas, rationale, and open questions so they do not
live only in conversation history. That document is context, **not implementation authorization**.
An idea must be promoted into a reviewed numbered-build contract before an agent may implement it.

## Current activation gate

Build 03's product contract may be reviewed while Build 02 is still being finished and accepted.
Do not send Build 03 to OpenCode Plan/Build mode until Build 02 is formally complete.

After Build 02 acceptance:

- mark Build 02 `Complete`;
- mark Build 03 `Active — ready for Plan mode`;
- keep later builds `Future`.

## Build discipline

For each build:

1. We decide user-visible behavior, non-goals, data/performance/platform constraints, and
   acceptance promises here in the repository.
2. The build contract must make clear how the slice preserves immediate common-path interaction and
   familiar/predictable user behavior; global priorities from `docs/DESIGN_PHILOSOPHY.md` apply even
   when a slice does not repeat them exhaustively.
3. The coding agent's Plan mode decides only the local implementation/test plan needed to satisfy
   that contract.
4. Build mode writes the smallest clear implementation and the tests that prove the promises.
5. Focused checks run during work; the full health gate runs before completion.
6. The owner reviews the diff for behavior, readability, scope, responsiveness, intuitiveness, and
   unnecessary complexity.
7. Only then does the next build become active.

Later build documents and `docs/FUTURE_IDEAS.md` do not authorize implementing their features
early.
