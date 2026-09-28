# ADR 0005 — Snapshot Trigger Evaluation

**Status:** Accepted for P0

## Decision
All triggers in an evaluation phase read the same frozen evaluated semantic
snapshot. Active direct, derived, and undefeated default supports may satisfy
their premises; defeated defaults remain provenance-only. Intermediate
mutations are not visible until patch commit.

## Rationale
This avoids nondeterminism caused by incidental rule iteration order and provides predictable concurrent effects.

## Consequence
Patch merging/conflict handling must be deterministic. More advanced concurrency semantics may be introduced later by explicit design.
