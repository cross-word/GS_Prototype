# S06 — Vampire / Sunlight

**Milestone:** Deferred (P2)

## Intent
"Vampires lose 5 health per second while exposed to sunlight."

## Required future semantics
A rate/continuous execution mode distinct from one-shot TRIGGER and truth-maintained DERIVE.

## Architectural constraint
Do not fake this in P0 by repeatedly firing an unbounded trigger without an explicit simulation-time model.
