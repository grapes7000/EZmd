# UI System

## Status

Accepted direction for Build 01 onward. The exact final visual profile is intentionally not
settled yet; the mechanism for comparing profiles is settled.

## UI technology

EZmd uses **PySide6 Qt Widgets**, not QML/Qt Quick, for the primary application UI.

The central writing surface is based on Qt's native text-document/widget stack so formatting,
selection, cursor behavior, undo/redo, and later Markdown serialization stay close to
`QTextDocument` rather than crossing a QML bridge.

Do not embed QML merely to obtain prettier controls. Do not add Qt WebEngine.

## Design goal

The document is the visual center of the application. Controls should remain small, peripheral,
and quiet enough that writing receives most of the attention.

The eventual EZmd look should be its own design. Existing repositories are reference material for
measurements and interaction ideas, not parent codebases to copy.

- `lab-workspace` contributes a compact, flat desktop density reference.
- `qt-app-template` contributes a consistent semantic-token approach and a somewhat roomier
  geometry reference.
- The third `Focus` profile explores hairline separation, low-chrome controls, and text-first
  hierarchy. It is inspired by characteristics the owner likes in contemporary editors, not an
  attempt to reproduce another application's UI.

## Semantic visual rules

User-facing visual measurements must not be scattered as unexplained pixel literals throughout
widget construction.

Centralize semantic roles for at least:

- spacing;
- content margins;
- control heights;
- border widths;
- corner radii;
- editor padding;
- typography sizes/weights where customized;
- component interaction states;
- color roles;
- optional depth/shadow levels.

The implementation may use a small dataclass, immutable mapping, named tuples, or another simple
representation. Do **not** build a general theme framework or plugin system.

Widget code should ask for meaning (for example, small spacing or control radius), not know why a
particular profile currently maps that meaning to 4 px or 8 px.

## Palette and geometry are separate concepts

Build 01 compares **geometry/interaction profiles**, not three unrelated color themes.

All three profiles should use the same initial semantic color roles so geometry can be compared
without color changes muddying the result. Color theming can evolve later without rewriting
geometry definitions.

The exact initial palette is provisional. Prefer Qt/system palette roles where they remain clear
and predictable; any custom colors must still live in one semantic palette definition rather than
inside individual widgets.

## Initial visual profiles

These are working design profiles, not promises that all three remain forever.

### Lab

Purpose: preserve the compact, flat density that worked well in `lab-workspace` without copying
its application code.

Reference geometry:

- very small toolbar/component gaps, around 1-4 px where adjacent controls form a group;
- common internal padding around 6 px;
- panel/content margin around 8 px;
- 1 px separators/borders;
- approximately 3 px input/editor corner radius;
- approximately 4 px button top-corner radius where a tab-like treatment is used;
- essentially flat depth: no decorative drop shadows.

The important character is compactness and crisp separation, not exact preservation of every old
stylesheet number.

### QTemp

Purpose: preserve the more systematic geometry used by `qt-app-template`.

Reference geometry:

- spacing scale: 4, 6, 8, 12, 16, 20, 24 px;
- small/normal control heights: approximately 26/30 px;
- radius scale: 4, 6, 8, 10 px;
- normal content margin around 20 px;
- 1 px borders;
- flat-to-low depth; separation is primarily surface/border based rather than shadow based.

The writing surface should not be wrapped in unnecessary cards merely because that template used
cards elsewhere.

### Focus

Purpose: explore the likely EZmd direction: text first, low chrome, compact controls, hairline
separation, and a distinctive but restrained modern desktop feel.

Working geometry/interaction rules:

- compact spacing centered around 4, 6, 8, 12, 16 px;
- normal controls around 26-28 px tall;
- small corner radius around 4 px, with larger radii used sparingly;
- 1 px hairline borders/separators;
- small outer/content margins so the document owns most of the window;
- no decorative drop shadows initially;
- ordinary toolbar/action buttons have **no visible outline at rest**;
- those quiet buttons gain a subtle hairline outline and/or restrained surface change on hover;
- keyboard focus must remain clearly visible even when resting mouse borders are hidden;
- pressed/checked states must be distinguishable without large filled pills.

`Focus` is the provisional default only so the project has a starting point. The presence of the
profile selector means changing the default later is cheap and expected.

## Application menu and formatting-toolbar placement

Build 02 establishes a clearer division between application commands and document-formatting
commands while keeping normal native window chrome.

The normal top application menu area contains:

- `File` → New, Open, Save;
- `Edit` → Undo, Redo;
- `View` → Visual Profile → Lab / QTemp / Focus.

Do not move these commands into a custom title bar. A native title bar plus normal application
menu bar remains the accepted cross-platform shell.

The formatting toolbar is reserved for writing/editing controls. Its settled Build 02 grouping is:

```text
↶ ↷ | Paragraph ▾ | B I S | • 1. Quote
```

Meaning:

1. Undo / Redo;
2. paragraph style (Paragraph/H1/H2/H3);
3. Bold / Italic / Strikethrough;
4. Bulleted list / Numbered list / Blockquote.

Use familiar curved-arrow visuals for Undo/Redo and preserve clear accessible names/tooltips.
The Strikethrough control should make its `S` visibly struck through while retaining the plain
accessible name/tooltip `Strikethrough`. No third-party icon pack is required for these controls.

New/Open/Save and the visual-profile choice do not occupy formatting-toolbar space from Build 02
onward.

## Blockquote presentation

A blockquote must look recognizably like quoted writing rather than merely like text that was
indented with Tab.

The semantic truth remains the document's quote state (`BlockQuoteLevel = 1` in the Build 02
model). Presentation must not insert a literal `|`, `>`, or other marker character into the user's
document and must not invent a second quote model.

The accepted visual treatment is deliberately restrained:

- a thin vertical hairline at the left of each quoted block;
- modest inset/padding between that hairline and the text;
- otherwise normal document typography, including any independent Paragraph/H1/H2/H3 style and
  Bold/Italic/Strikethrough formatting;
- no card, large filled background, decorative shadow, or automatic italicization.

The hairline is presentation only. Its width/spacing/color should come from existing semantic
profile/palette roles where practical instead of unrelated hard-coded styling. Lab, QTemp, and
Focus may express the same quote treatment at their existing density, but switching profiles must
not change quote semantics or document history.

Prefer the smallest verified Qt-native/rendering approach that keeps quote presentation separate
from document meaning. Do not add visible marker characters, HTML persistence, or a generalized
custom-document rendering framework merely to draw the hairline.

## Runtime profile selection

Build 01 introduced live switching for `Lab`, `QTemp`, and `Focus` through a compact toolbar
selector so the geometry profiles could be compared quickly.

From Build 02 onward, profile selection moves to `View > Visual Profile` to keep the formatting
bar focused on document editing.

Requirements remain:

- switching applies immediately without restarting;
- switching must not change document text, rich formatting, cursor position, selection, undo
  history, or current file;
- the selection UI is deliberately simple and local; it does not justify a plugin/theme
  marketplace;
- persistence across restarts is deferred unless a later build explicitly adds settings
  persistence.

If profile selection is represented in more than one place in a future build, all representations
must share the same underlying action/state rather than duplicate profile logic.

## Styling boundaries

Visual-profile code owns visual tokens and stylesheet/palette application.

It does **not** own:

- document loading/saving;
- Markdown conversion;
- editor formatting semantics;
- search;
- settings storage;
- feature registration.

The main window should compose controls; it should not become a giant stylesheet/string store.

## Accessibility and interaction

Low chrome must not mean low discoverability.

- Keyboard focus remains visible.
- Standard Qt keyboard shortcuts should be used where available.
- Hover-only decoration may supplement, but must not replace, focus/checked/disabled states.
- Text contrast must remain readable.
- Controls should remain usable at common desktop scaling factors.
- Familiar commands such as Undo/Redo should retain recognizable visual language rather than
  requiring the user to relearn common desktop conventions.
- Semantic formatting should be visually distinguishable enough that users do not need to infer
  hidden state from toolbar controls alone; blockquotes are the first explicit example.

## What is deliberately deferred

- final color palette;
- final default geometry profile;
- light/dark theme switching;
- user-authored themes;
- theme import/export;
- animated transitions;
- custom title bars/window chrome;
- shadow/depth effects beyond the semantic placeholder;
- icon library selection;
- user-customizable toolbar layout.

Deferred UI ideas and their current rationale are recorded in `docs/FUTURE_IDEAS.md`.
