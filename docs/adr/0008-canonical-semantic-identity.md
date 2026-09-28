# ADR 0008 — Canonical Semantic Identity

**Status:** Accepted for P0

## Decision

Numerically equal `NumberValue` values are semantically equal for deterministic
identity generation. P0 serializes numeric arguments in one canonical decimal
form, so `NumberValue(1)` and `NumberValue(1.0)` yield the same canonical
proposition and derived/default/trigger identities.

## Rationale

Python's textual representations distinguish forms that the P0 value model
compares as equal. Semantic identity must not vary with that incidental format.

## Consequence

Deterministic IDs and revision payloads use canonical propositions rather than
raw object `repr()` for semantic argument content.
