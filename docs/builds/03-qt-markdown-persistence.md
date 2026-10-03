# Build 03 — Qt Markdown persistence

Status: approved next slice; not implemented on main.

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

Write the resulting UTF-8 text through the existing safe file writer.

Saving must:

- write to the existing document path for normal Save;
- use the existing Save dialog for a new untitled document;
- mark the document clean only after the write succeeds;
- leave the cursor and selection where they were;
- leave formatting and Undo/Redo history unchanged;
- not rewrite the live QTextDocument merely to produce output.

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

Use Qt exactly as the file conversion layer for this build.

Do not add:

- Pyromark;
- another Markdown library;
- a custom parser;
- a custom serializer;
- regular-expression Markdown rewriting;
- an allowlist or denylist;
- a Markdown AST;
- a synchronized source buffer;
- a compatibility layer;
- HTML as a hidden persistence format;
- a new production dependency.

If Qt has odd behavior for a feature EZmd does not expose, ignore it for this build.

If an EZmd-supported feature fails the required save/reopen round-trip, stop and report the smallest reproduction before adding workaround code.

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
- Save does not move the cursor or destroy the selection;
- failed read leaves the existing document, path, and state intact;
- failed write leaves the document modified and preserves the old file;
- .txt still opens and saves as plain text;
- ordinary typing, cursor movement, toolbar synchronization, and profile switching do not invoke Markdown conversion;
- existing Build 01 and 02 tests remain green.

Do not build a giant Markdown test matrix. Qt's support for features EZmd does not expose is outside this build's automated contract.

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
