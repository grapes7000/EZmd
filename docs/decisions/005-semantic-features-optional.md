# 005 — Semantic Features Remain Optional

## Status

Accepted.

## Context

Semantic matching could create useful note connections but introduces heavier model/runtime/index
costs than ordinary writing/search/wiki linking requires.

## Decision

Semantic search and embeddings are outside the initial twelve builds and must never become
requirements for basic editing, full-text search, wiki links, backlinks, or graph view.

## Why

Normal writing should remain fast, understandable, offline-friendly, and small. Lightweight
explicit/lexical relationships should be proven before adding model infrastructure.

## Alternatives considered

Bundled local embedding model; remote AI API; no semantic functionality ever.

## Consequences

The first connection-suggestion system uses lightweight local techniques only. Any later semantic
feature must remain optional and isolated from core startup/typing paths.
