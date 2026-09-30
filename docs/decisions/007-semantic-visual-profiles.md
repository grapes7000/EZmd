# 007 — Semantic Visual Profiles

## Status

Accepted.

## Context

The owner wants to compare several useful visual geometries while developing EZmd and does not want
spacing, rounding, borders, depth, or control-state rules hard-coded throughout widget code.

## Decision

Use one small semantic visual-profile system. Build 01 provides three runtime-selectable profiles:
Lab, QTemp, and Focus.

Geometry/interaction roles and color roles remain conceptually separate. Widgets consume semantic
roles; profile definitions own the measurements.

## Why

- The app can compare/tune visual direction without refactoring behavior.
- It prevents arbitrary pixel literals from drifting across screens.
- It lets EZmd borrow useful measurements/interaction ideas without copying application-specific UI
  code from reference repositories.
- It supports a unique final design instead of locking the first screen into one reference look.

## Alternatives considered

- Hard-code values inside each widget: rejected because later design iteration would require broad
  edits.
- Copy `lab-workspace` UI code: rejected because that code is tied to its lab-specific panels,
  source/preview model, and other project behavior.
- Copy the full `qt-app-template` QML shell: rejected because QML is not the chosen primary UI.
- General theme/plugin engine: rejected as unnecessary architecture.

## Consequences

- Build 01 includes a small live profile switcher.
- Profile switching must not replace/mutate document state.
- The final default profile may change later without changing application logic.
- Visual profiles are not a promise of user-importable themes or a plugin marketplace.
