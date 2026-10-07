# Build 04 — Desktop workspace

Status: active umbrella build; implementation proceeds through small approved slices on stacked
development branches.

## Purpose

Build 04 turns EZmd from a durable visual editor into a complete native writing workspace.

The build intentionally combines three kinds of work:

- desktop shell and visual-system refinement;
- ordinary desktop-editor completeness;
- workspace and navigation capabilities.

These are one product effort. They are not required to run as three sequential phases.

## Development rule

Build 04 is an umbrella contract, **not** permission to implement the whole roadmap at once.

Each code task must still:

1. have a focused owner-approved scope;
2. preserve the existing working editor and Markdown safety boundaries;
3. remain launchable;
4. add focused tests where behavior changes;
5. receive owner visual/manual acceptance when appropriate;
6. stop when that slice is complete.

A later Build 04 slice may come from any of the three areas if it is the smallest useful next step.

## Current baseline

Production `main` contains Builds 01-03.

Build 03 Markdown persistence is merged and used as the file-format baseline. Its Windows
round-trip/CI issue is known deferred acceptance debt and is not the active Build 04 task.

## Current stacked implementation

### 04.01 — Design tokens and themes

Branch: `build/04-01-design-tokens`

Implemented there:

- compact spacing, radius, border, and control-size tokens suitable for Qt Widgets;
- a Compact visual profile;
- built-in Light and Dark themes;
- semantic color roles derived from the owner's `qt-app-template` visual language.

### 04.02 — Editor pane and sidebar shell

PR #8 has been merged into `build/04-01-design-tokens`.

Implemented there:

- the formatting toolbar lives inside a dedicated editor pane above the editor instead of occupying
  the whole `QMainWindow` toolbar area;
- a left Documents sidebar shell;
- splitter-based resizing;
- collapse to a narrow rail;
- complete hide/show from View;
- keyboard-accessible sidebar controls;
- preservation of editor/document state while shell visibility changes.

Document navigation is deliberately not part of this slice.

The stacked Build 04 branch has not yet been merged into production `main`.

## Remaining Build 04 areas

These are directions, not an implementation order.

### Shell and visual presentation

- centered page-like writing surface;
- narrow-window behavior for that surface;
- continued toolbar/sidebar visual refinement;
- top-left application/menu direction;
- subtle development/status strip that makes the running build identifiable.

US Letter proportions may guide presentation, but this does not authorize durable page-size,
margin, or pagination metadata.

### Desktop completeness

Potential focused slices include:

- Save As;
- ordinary editing commands and shortcuts;
- recent/open flows;
- drag/drop where useful;
- links behaving naturally;
- clear feedback and sensible dialogs;
- small desktop expectations discovered through real use.

### Workspace and navigation

Potential focused slices include:

- simple document navigation in the existing sidebar shell;
- full-text search;
- quick open;
- links and link navigation;
- backlinks/related documents only after the simpler link workflow exists.

## Architecture boundaries

Build 04 keeps:

- PySide6 + Qt Widgets;
- one live Qt `QTextDocument` as the editable document state;
- Markdown conversion at Open/Save only;
- safe file replacement and unsaved-change protection;
- presentation separate from document meaning.

Build 04 does not justify:

- QML/Qt Quick as a second UI stack;
- WebEngine or a browser runtime;
- a hidden database merely to draw the workspace shell;
- a plugin framework;
- a custom Markdown parser/serializer;
- a shadow editable document model;
- durable page-layout metadata solely for visual styling.

## Visual-system reference

The owner's `qt-app-template` is a visual-system reference, not a codebase to transplant.

Useful ideas include semantic palette roles, compact spacing, restrained radii, control heights,
separators, quiet hover/selection states, and consistent focus treatment.

Keep the implementation native to Qt Widgets and small enough to teach from.

## Known debt

The Windows Build 03 Markdown CI problem is intentionally deferred. Record it and avoid regressing
it, but do not let unrelated Build 04 slices grow into a persistence rewrite.

## Stop condition for each slice

When the approved user-visible behavior works, focused tests pass, and the owner accepts the
interaction/visual result, stop. Choose the next Build 04 slice separately.
