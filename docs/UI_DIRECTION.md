# UI direction

Status: active Build 04 direction. Parts of this direction are already implemented on stacked
development branches; the document is not a command to implement every remaining item.

## Purpose

Build 04 establishes EZmd as a recognizable native desktop writing workspace while ordinary desktop
usability and workspace capabilities grow alongside the shell.

Visual-system work, desktop completeness, and workspace/navigation are parts of the same build.
They may be interleaved in small slices.

## Current development state

On the stacked Build 04 branch:

- semantic spacing/radius/control tokens and built-in Light/Dark themes exist;
- the formatting toolbar belongs to a dedicated editor pane;
- a left Documents sidebar shell is resizable, collapsible to a rail, and completely hideable.

Those changes are not yet on production `main`.

The sidebar does not yet provide document navigation.

## Visual direction

EZmd should remain a compact native desktop writing workspace with:

- a quiet left document/sidebar region;
- a large main writing workspace;
- a compact action/formatting strip belonging to the writing pane;
- a centered page-like writing surface;
- a restrained application/menu hierarchy;
- a subtle development/status strip while useful;
- restrained borders, spacing, radii, and neutral surfaces.

The app should share visual DNA with the owner's `qt-app-template` without looking like the same
application.

That shared DNA includes:

- semantic color roles rather than arbitrary per-widget colors;
- compact spacing increments;
- restrained 4-8 px style radii for ordinary controls;
- approximately 30 px control heights where appropriate;
- 1 px separators/hairlines for structural regions;
- small desktop-oriented type sizes;
- quiet hover/selection states;
- consistent focus treatment.

## Writing surface

The main editor should not simply fill the workspace edge to edge forever.

The intended direction is a centered page-like writing surface with proportions influenced by
standard US Letter paper (8.5 x 11). This is presentation, not a new Markdown document feature.

A focused slice must still decide the exact behavior before implementation, including:

- continuous constrained writing column versus visibly paginated pages;
- default visual padding/margins;
- narrow-window behavior;
- width constraints or scaling;
- light/dark surface treatment;
- whether any presentation option is user-configurable.

Do not add durable page-size or margin metadata to Markdown merely to achieve this appearance.

## Sidebar and workspace

The sidebar shell is already established in stacked Build 04 work.

Later Build 04 slices may add:

- document/file navigation;
- quick open;
- search;
- links and link navigation;
- related-document/backlink workflows after simpler navigation/linking proves useful.

Do not build a generic workspace framework in advance of those concrete needs.

## Desktop completeness

Build 04 also includes ordinary desktop-editor behavior. These features do not have to wait until
the visual shell is "finished."

Examples include Save As, predictable shortcuts, editing commands, recent/open flows, drag/drop,
clear feedback, sensible dialogs, and other expectations discovered through use.

Choose them as focused slices when they are the most useful next improvement.

## Application menu direction

The traditional menu bar may later be replaced or visually deemphasized by a top-left application
control inspired by modern native editors.

That control may expose familiar File, Edit, View, Settings, and About actions while standard
keyboard shortcuts remain available.

Do not replace the current menus until a focused task defines native Qt behavior and platform
expectations.

## Development/status strip

A subtle bottom strip may be useful during development so the owner can identify the running build
and avoid confusing an old checkout with current work.

Possible content includes the active build slice, development state, and branch/commit information
when it can be reported reliably.

Whether a user-facing status bar remains in the final product is undecided.

## Relationship to qt-app-template

`qt-app-template` is a visual-system reference, not a drop-in UI implementation for EZmd.

Its QML components should not be copied into EZmd as runtime UI code. EZmd remains Qt Widgets.

Reuse principles and values where they improve consistency: semantic palette roles, spacing, radius,
typography/control sizing, separators, and interaction treatment.

Do not introduce QML, a second UI stack, or a generic design-system framework merely to share these
values.

## Slice rule

Every Build 04 implementation step still needs a focused owner-approved task. The task should state
the user-visible goal, exact scope, tests/acceptance expectations, and what remains out of scope.

Keep each slice small and launchable.
