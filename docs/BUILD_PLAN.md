# Build plan

EZmd is developed in small launchable slices. A build should add one visible capability, keep the
application runnable, add focused tests, and stop.

## Completed

### Build 01 — Native editor shell

New/Open/Save, safe UTF-8 files, unsaved-change protection, native window, and visual profiles.

### Build 02 — Formatting toolbar

Paragraph/H1/H2/H3, bold, italic, strikethrough, bullet and numbered lists, blockquotes, and native
Undo/Redo.

## Reset

### Build 03 — Durable rich-document persistence

The earlier Build 03 designs and experiments are not accepted production work.

Before writing Build 03 again, the owner will decide:

- which durable file format best fits EZmd;
- what "portable" must mean in practice;
- which formatting must survive round-trip;
- whether native Qt conversion is sufficient;
- what evidence would justify any additional parser/serializer dependency or code.

Until that discussion is complete, there is no Build 03 implementation contract.

## Later work

Sidebar, search, quick-open, links, backlinks, encryption, and other ideas remain uncommitted future
work. They will receive their own build contract only when they become the next task.
