# ADR 0002 — Four-State Support Semantics

**Status:** Accepted for P0

## Decision
Propositions derive effective status from independent positive and negative supports:
UNKNOWN, TRUE_ONLY, FALSE_ONLY, CONFLICT.

The default world assumption is open-world.

## Rationale
The game must distinguish "false" from "not yet defined" and must preserve contradictions without invalidating the entire world.

## Consequence
The runtime is intentionally paraconsistent in the limited sense that contradiction does not imply arbitrary propositions.
