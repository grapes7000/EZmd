# Glossary

Plain-language definitions for terms used by the project.

## Source of truth

The authoritative copy of data. Other copies may be deleted and rebuilt from it.

## Cache

Disposable data kept because recomputing it every time would be slower.

## Index

A rearranged representation of information that makes searching faster.

## Full-text search

Searching through the actual words inside documents rather than only filenames.

## Fuzzy search

Matching text even when the typed query is incomplete or not an exact character-for-character
match.

## Round-trip

Opening data, editing it, and saving it again without losing or unexpectedly changing supported
information.

## Vertical slice

A small feature increment that reaches from internal logic to a visible, testable user outcome
while leaving the app runnable.

## Derived data

Information produced from user documents, such as a search index or graph cache. Derived data is
not the authoritative copy.

## Build contract

The reviewed document for one numbered build. It states what the user should get, what is in/out
of scope, what must be tested, and the important safety/performance/platform constraints. A coding
agent implements the contract; it does not rewrite it during Plan mode.

## Semantic visual token

A named visual role such as `small spacing`, `control radius`, or `hairline border`. Widget code
uses the role instead of repeating unexplained raw numbers.

## Visual profile

A coherent set of semantic visual-token values and component-state rules. Build 01 includes Lab,
QTemp, and Focus so their geometry can be compared without changing document behavior.

## Health gate

The one complete repository verification pass: formatting/linting, typing, tests, smoke checks,
and cheap safety checks. EZmd's cross-platform gate lives in `bin/check.py`.
