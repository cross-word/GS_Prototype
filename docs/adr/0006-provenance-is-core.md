# ADR 0006 — Provenance Is a Core Requirement

**Status:** Accepted for P0

## Decision
Support justification and revision provenance are required semantic infrastructure, not optional debug logging.

## Rationale
The intended gameplay includes observing unexpected outcomes and asking why they happened. Reliable explanation must come from runtime traces rather than LLM inference.

## Consequence
Implementations that compute correct truth status but discard justification are non-conforming.
