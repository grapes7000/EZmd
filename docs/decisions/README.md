# Architecture Decision Records

Decision records explain *why* an architectural choice exists so future contributors/coding agents
do not reopen settled questions accidentally.

Statuses:

- **proposed** — not yet settled; implementation must not assume it is final;
- **accepted** — project authority unless a later decision explicitly supersedes it;
- **superseded** — replaced by a later decision;
- **rejected** — considered and intentionally not chosen.

A coding agent may point out a concrete technical conflict with an accepted decision, but it must
not silently replace that decision during Plan or Build mode.

Current accepted baseline:

1. native PySide6/Qt UI;
2. Markdown as the normal durable source of truth;
3. no WebEngine in the core editor;
4. search indexes are disposable derived data;
5. semantic/model features remain optional;
6. Qt Widgets are the primary UI, not QML/Qt Quick;
7. semantic visual profiles centralize geometry/interaction rules;
8. Linux/macOS/Windows are first-class from the first build.
