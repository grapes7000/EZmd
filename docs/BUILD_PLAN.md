# Build Plan

Every numbered build is a **product contract** decided before coding begins. OpenCode Plan mode may
plan how to implement the active contract; it may not redesign the roadmap or add adjacent
features.

Every completed build must leave the application runnable and testable.

| Build | Slice | Main result |
|---|---|---|
| 01 | Native editor shell | Cross-platform Qt Widgets editor with safe basic file actions and live visual-profile switcher |
| 02 | Formatting toolbar | Familiar Word-like formatting controls |
| 03 | Markdown round-trip | Open/save the supported rich-document subset as predictable Markdown |
| 04 | Document sidebar | Browse folders and notes |
| 05 | Full-text search | Fast search across note contents |
| 06 | Fuzzy Quick Open | Instant keyboard-driven note opening |
| 07 | Wiki links | Link notes to other notes |
| 08 | Backlinks | See which notes refer to the current note |
| 09 | Search-and-link | Safely create links across multiple notes |
| 10 | Explicit-link graph | Visualize real wiki-link relationships |
| 11 | Connection suggestions | Find lightweight lexical/topic relationships |
| 12 | Encryption at rest | Protect opted-in private storage correctly |

Optional semantic/embedding work is outside the first twelve builds.

## Build discipline

For each build:

1. We decide user-visible behavior, non-goals, data/performance/platform constraints, and
   acceptance promises here in the repository.
2. The coding agent's Plan mode decides only the local implementation/test plan needed to satisfy
   that contract.
3. Build mode writes the smallest clear implementation and the tests that prove the promises.
4. Focused checks run during work; the full health gate runs before completion.
5. The owner reviews the diff for behavior, readability, scope, and unnecessary complexity.
6. Only then does the next build become active.

Later build documents do not authorize implementing their features early.
