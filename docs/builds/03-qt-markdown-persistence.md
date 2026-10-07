# Build 03 — Qt Markdown persistence

Status: implementation merged into `main`; final acceptance remains open because the Windows CI round-trip issue is unresolved.

The merged implementation is the production persistence baseline. Linux and macOS CI have passed this contract. Windows CI still exposes a Build 03 Markdown round-trip problem and can time out after a blocking Save failure dialog. The owner has intentionally deferred that investigation while Build 04 continues. Do not weaken the round-trip safety contract merely to make that CI job green.

## User outcome

A user can:

1. open an EZmd document;
2. see a normal visual document rather than Markdown punctuation;
3. type and use the existing formatting toolbar;
4. save;
5. close the application;
6. reopen the same document;
7. see the same supported text and formatting.

The user should not need to know what Markdown is.

If native Qt conversion would change the live document's supported meaning, Save must report a
normal failure without replacing the existing file or altering the live document.

## Scope

Build 03 does one thing: make the formatting already implemented in Build 02 durable.

Supported product vocabulary for this slice:

- Paragraph;
- H1;
- H2;
- H3;
- Bold;
- Italic;
- Strikethrough;
- bulleted list;
- numbered list;
- blockquote.

This is the set EZmd promises through its own UI in Build 03. Qt may understand additional Markdown constructs, but Build 03 does not add controls, compatibility code, or product promises for them.
External Markdown outside this product vocabulary is best-effort; opening it does not imply EZmd
can safely save every construct it contains. Save verification refuses a lossy write.

### Safe formatting profile

The 192-state exploratory matrix established the smaller, lossless Build 03 profile:

- Paragraph may have no list, Bullet, or Numbered with Quote off, or Quote with no list. Its inline
  modes may be none, Bold, Italic, Bold + Italic, or Strikethrough alone.
- H1/H2/H3 are standalone blocks: no list or Quote, with Bold on. Heading Italic and
  Strikethrough are unavailable. These are **23 distinct supported semantic states**.
- Quote + Heading is excluded **because Qt Markdown cannot reliably round-trip it**, not
  because it would be an undesirable writing experience. Applying Quote to a heading changes
  that block to Paragraph with Quote; requesting a heading on a quoted Paragraph leaves it
  Paragraph. Bold remains an ordinary inline mode on that Paragraph.
- Applying Bullet/Numbered to a heading first makes it Paragraph; applying a heading to a list
  removes the list. Applying Quote to a list removes the list; applying a list to Quote removes
  Quote. Changing list type retains a Paragraph. Switching to Strike
  clears Bold and Italic; switching to Bold or Italic clears Strike. A heading cannot turn Bold
  off. The toolbar reflects the resulting document state.
- Enter after text in a heading begins a Paragraph. Enter after text in a list or quote continues
  that structure as Paragraph. Enter on a blank structured block exits the list or quote.
  Inline modes persist across Enter until the user turns them off.

Qt Markdown also drops leading spaces and empty paragraphs. A focused encoder on a temporary
document preserves those during Save; Open decodes them on its temporary document. The file
uses a reserved invisible marker and a recognizable comment header only when needed. Literal
markers are escaped. Save verification still refuses any real text or formatting loss. In
particular, Qt may lose list membership from the first of two consecutive heading-list items or
Quote at an adjacent list boundary. These combinations are unavailable via the toolbar; external
Markdown with them still receives strict Save verification.

## Required implementation

### Open .md and .markdown

Use the existing UTF-8 file reader.

Create or load a Qt document with QTextDocument.setMarkdown(...). The parsed document becomes the document shown by the existing editor.

Opening must:

- preserve the current document if reading or loading fails;
- leave the opened document unmodified and clean;
- leave no conversion operation in user Undo history;
- reconnect any document signals the window relies on after replacing the document;
- keep the existing toolbar state synchronized with the loaded document;
- keep normal focus behavior.

Do not inspect the Markdown first to decide whether syntax is allowed.

### Save .md and .markdown

Serialize the live document with QTextDocument.toMarkdown().

Where necessary, clone the live document and encode only otherwise-lost whitespace before
Qt's native toMarkdown(). Parse the result with a temporary QTextDocument.setMarkdown(...),
decode the reserved markers, and compare supported meaning:
visible text, Paragraph/H1/H2/H3, list type, quote state, and Bold/Italic/Strikethrough runs.
Write the resulting UTF-8 text through the existing safe file writer **only when equivalent**.

Saving must:

- write to the existing document path for normal Save;
- use the existing Save dialog for a new untitled document;
- mark the document clean only after the write succeeds;
- leave the cursor and selection where they were;
- leave formatting and Undo/Redo history unchanged;
- not rewrite the live QTextDocument merely to produce output.
- preserve the old file, modified state, path, cursor, selection, formatting, and Undo/Redo
  history when verification fails;
- report a normal user-facing Save failure when verification fails.

Only Save performs this verification. Typing, formatting actions, cursor movement, toolbar
synchronization, normal Undo/Redo, and visual-profile changes never convert Markdown.

A new document saved without an explicit text-file choice should become an EZmd Markdown-backed document. The UI should not teach the user Markdown terminology just to accomplish this.

### Plain text

Keep .txt as plain text for this slice:

    .txt open  → setPlainText(...)
    .txt save  → toPlainText()

Do not redesign text-file behavior in Build 03.

## User-facing Markdown invisibility

Normal editing remains visual.

Do not add:

- source mode;
- preview mode;
- Markdown punctuation overlays;
- Markdown syntax hints;
- Markdown-specific toolbar labels;
- warnings about unsupported Markdown extensions;
- a Markdown settings page.

Use ordinary product language such as "document", "heading", "bold", "list", and "quote".

Where practical, display .md and .markdown documents by their filename stem in the window title rather than emphasizing the extension. Do not fight the operating system if its file dialog chooses to show real extensions.

## Native-first rule

Use Qt as the Markdown conversion layer for this build. A narrow, approved whitespace-only
encoding around Open/Save is the sole exception; it does not change formatting semantics.

Do not add:

- Pyromark;
- another Markdown library;
- a custom parser;
- a custom serializer;
- general-purpose or regular-expression Markdown rewriting;
- an allowlist or denylist;
- a Markdown AST;
- a synchronized source buffer;
- a compatibility layer;
- HTML as a hidden persistence format;
- a new production dependency.

The focused whitespace encoder/decoder is limited to leading spaces, empty or whitespace-only
paragraphs, and literal-marker escaping. Do not extend it to unsupported formatting states.

If Qt has odd behavior for a feature EZmd does not expose, ignore it for this build.

If a document still fails round-trip verification, do not write it. Do not add
formatting-specific Markdown rewriting to make it pass.

## Expected production change

The change should stay small.

Expected production work is primarily in src/ezmd/ui/main_window.py.

A small focused helper is acceptable only if it makes the file lifecycle easier to understand. Do not create markdown.py merely to wrap setMarkdown() and toMarkdown().

No dependency change is expected.

## Automated acceptance

Add focused tests proving:

- a Markdown document containing representative Build 02 formatting opens as formatted Qt document state;
- the opened document is clean;
- opening does not create user Undo history;
- editing the opened document still uses normal native Undo/Redo;
- Save writes Markdown rather than plain visible text;
- Save and reopen preserves representative Paragraph/H1/H2/H3, bold, italic, strikethrough, bullet, numbered-list, and blockquote meaning;
- all 23 supported formatting states survive real Save/Open; each of the 192 attempted toolbar
  combinations either yields one of those safe states or is normalized without silent loss;
- failed Markdown verification leaves the file and live document unchanged;
- typed leading spaces, trailing empty paragraphs, blank or whitespace-only paragraphs, and
  multiple blank lines survive Save/Open without relaxing formatting verification;
- heading/list/quote exclusivity, Enter rules, and inline typing modes remain synchronized;
- adjacent supported blocks and consecutive would-be heading-list items have Save/Open regressions;
- Save does not move the cursor or destroy the selection;
- failed read leaves the existing document, path, and state intact;
- failed write leaves the document modified and preserves the old file;
- .txt still opens and saves as plain text;
- ordinary typing, cursor movement, toolbar synchronization, and profile switching do not invoke Markdown conversion;
- existing Build 01 and 02 tests remain green.

The exploratory 192-state matrix is retained as a normalization and persistence safety gate, not
as a requirement to support every requested combination. Qt's support for features EZmd does
not expose is outside the automated contract.

## Manual owner acceptance

After the full automated gate passes, launch the real application and verify:

1. Create a new document.
2. Type several paragraphs.
3. Apply H1/H2/H3, bold, italic, strikethrough, bullets, numbering, and blockquote.
4. Save it without needing to interact with Markdown syntax.
5. Close the document or application.
6. Reopen the saved document.
7. Confirm the visible text and each formatting type still look and behave the same.
8. Edit the reopened document, Undo/Redo, save again, and reopen again.
9. Open one ordinary external Markdown file containing only common and basic formatting and confirm it behaves reasonably.
10. Confirm the normal interface still feels like a writing app rather than a Markdown editor.

Build 03 is complete only after this owner pass and Linux, macOS, and Windows CI succeed.

## Stop condition

When the required behavior works and tests pass, stop.

Do not continue into links, images, tables, task lists, code blocks, footnotes, math, workspace features, UI redesign, or Markdown compatibility work. Those need later product decisions or slices.
