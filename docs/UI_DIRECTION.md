# UI direction

Status: approved direction for the work immediately after Build 03 acceptance. This is not yet a
detailed implementation plan.

## Purpose

After Build 03 is accepted, stop expanding Markdown behavior and move into desktop application
structure and visual design.

The next UI work should establish a recognizable EZmd shell before adding workspace features such
as search, backlinks, or larger navigation systems.

## Approved visual direction

EZmd should move toward a compact native desktop writing workspace with:

- a quiet left document/sidebar region;
- a large main writing workspace;
- a compact top action/formatting strip;
- a top-left application/menu control inspired by editor applications such as Zed;
- a subtle bottom development/status strip;
- restrained borders, spacing, radii, and neutral surfaces;
- a centered writing surface inside the main workspace.

The app should share visual DNA with the owner's qt-app-template without looking like the same
application.

That shared DNA means reusing design rules such as:

- semantic color roles rather than arbitrary per-widget colors;
- compact spacing increments;
- restrained 4-8 px style radii for ordinary controls;
- approximately 30 px control heights;
- 1 px separators/hairlines for structural regions;
- small desktop-oriented type sizes;
- quiet hover/selection states;
- consistent focus treatment.

The exact token set and values will be planned before implementation.

## Layout direction

The sidebar should eventually be:

- resizable;
- collapsible;
- completely hideable;
- suitable for a simple file/document tree first;
- able to grow into later workspace navigation without requiring a new window architecture.

The main writing area should not simply fill the entire workspace edge to edge.

The intended direction is a centered page-like writing surface with proportions based on standard
US Letter paper (8.5 x 11). This is initially a presentation decision, not a new Markdown document
feature.

Before implementation, the plan must decide:

- whether the surface is one continuous Letter-width writing column or visually paginated pages;
- the default visual margins/padding;
- narrow-window behavior;
- how the surface scales or constrains width;
- light and dark surface colors;
- whether any page/margin options are user-configurable.

Do not add durable page-size or margin metadata to Markdown merely to achieve the visual design.
If real document page layout becomes a product requirement later, it requires a separate storage
decision.

## Application menu direction

The current traditional menu bar may later be replaced or visually deemphasized by a top-left
application control.

That control can expose familiar desktop actions such as File, Edit, View, Settings, and About
while keeping standard keyboard shortcuts available.

The exact native Qt implementation and platform behavior must be planned before replacing the
existing menus.

## Development/status strip

Keep a subtle bottom strip during development.

Its primary development purpose is to make the running build immediately identifiable so the owner
can detect accidentally launching an older checkout or build.

A useful development label may include:

- active build slice;
- development state;
- optionally version or branch/commit information when that can be shown reliably.

Do not make unverified product/security claims in this strip.

Whether a user-facing status bar remains in the final product can be decided later.

## Relationship to qt-app-template

qt-app-template is a visual-system reference, not a drop-in UI implementation for EZmd.

The template currently uses PySide6 with Qt Quick/QML, while EZmd deliberately uses Qt Widgets.
Its QML components therefore should not be copied into EZmd as runtime UI code unless the project
explicitly changes its UI architecture.

The useful reusable material is primarily:

- semantic palette roles;
- spacing scale;
- radius scale;
- typography scale;
- control-size conventions;
- separator and state-treatment rules;
- interaction ideas such as quiet sidebar rows and active-state markers.

Before implementation, inspect the template's current tokens and decide which values become
EZmd-native Qt Widgets constants or styling rules.

Do not introduce QML, a second UI stack, or a generic design-system framework only to share these
values.

A small Widgets-native token/style module is acceptable later if the implementation plan shows it
reduces duplicated styling and keeps the code easier to understand.

## Current boundaries

This direction does not yet authorize production UI changes.

Before coding, create a focused implementation plan that settles:

- the first UI slice and exact scope;
- the Widgets layout structure;
- sidebar ownership and resize/collapse behavior;
- writing-surface geometry;
- the application-menu approach;
- status-strip contents;
- the subset of qt-app-template tokens to adopt;
- dark/light behavior;
- tests and owner visual acceptance.

Keep the first implementation slice small and launchable.
