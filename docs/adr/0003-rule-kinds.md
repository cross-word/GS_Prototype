# ADR 0003 — Separate DERIVE, DEFAULT, and TRIGGER

**Status:** Accepted for P0

## Decision
P0 distinguishes three rule semantics:
- DERIVE: truth-maintained logical support;
- DEFAULT: defeasible logical support;
- TRIGGER: snapshot-based persistent mutation through WorldPatch.

## Rationale
`Bird -> Animal` and `Glass hits ground -> Glass breaks` look syntactically similar but have fundamentally different persistence semantics.

## Consequence
Rule APIs and tests must preserve this distinction. Continuous/rate dynamics are deferred.
