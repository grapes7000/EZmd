# Architecture Tests

Keep this directory intentionally small.

Candidate/accepted boundaries are added only when the corresponding architecture exists. Early
examples include:

- production code does not import Qt WebEngine;
- the primary UI does not import Qt QML/Qt Quick modules;
- lower-level document behavior does not depend on visual-profile modules;
- core writing behavior does not introduce network access.

Prefer behavioral/integration tests when they can prove the guarantee without brittle source-code
inspection.
