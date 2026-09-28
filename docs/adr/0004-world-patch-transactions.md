# ADR 0004 — Atomic WorldPatch Transactions

**Status:** Accepted for P0

## Decision
Persistent world mutation occurs only through validated atomic WorldPatch commits.

## Rationale
Partial interpretation of a player request must not leave the world half-mutated. Atomic commits also provide a clean basis for undo, forks, replay, and provenance.

## Consequence
Contradiction may be committed if structurally valid; contradiction alone is not transaction failure.
