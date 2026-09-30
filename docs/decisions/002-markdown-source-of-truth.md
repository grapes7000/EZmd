# 002 — Markdown as Source of Truth

## Status

Accepted.

## Context

Documents should remain portable, durable, understandable, and useful outside EZmd.

## Decision

Plain Markdown files are the default authoritative document format.

While a document is open, Qt's document model is the editable in-memory state. Saving converts the
supported formatting subset back to Markdown. Derived caches/databases are never the only copy of
normal user documents.

## Why

This preserves interoperability and avoids trapping user writing inside an application-specific
primary database or rich-text format.

## Alternatives considered

HTML, rich-text serialization, proprietary document format, SQLite-owned documents.

## Consequences

- The supported formatting vocabulary must remain intentionally constrained.
- Build 03 must define and test canonical Markdown round-trip behavior.
- Exact author marker choices such as `*` versus `_` need not be preserved if intentional
  normalization is documented and tested.
