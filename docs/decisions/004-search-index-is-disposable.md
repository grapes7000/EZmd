# 004 — Search Index Is Disposable

## Status

Accepted.

## Context

Full-text search should be fast without turning a database into the owner of user documents.

## Decision

Search data is derived from authoritative Markdown and must be safe to delete/rebuild.

## Why

A broken/missing index should cost time to rebuild, not user writing. This also keeps the core file
format usable outside EZmd.

## Alternatives considered

Database-owned documents; rescanning every file on every search.

## Consequences

Index rebuild behavior becomes a required tested capability in Build 05. Later encryption must
also account for plaintext index leakage rather than pretending a disposable index is harmless.
