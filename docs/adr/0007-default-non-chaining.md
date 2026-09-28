# ADR 0007 — DEFAULT Non-Chaining

**Status:** Accepted for P0

## Decision

P0 evaluates DEFAULT premises only against ordinary support: direct support and
DERIVE support. A DEFAULT support never satisfies another DEFAULT premise in the
same semantic evaluation.

## Rationale

This makes a default a defeasible proposal grounded in the ordinary semantic
view, rather than an iterative source of further assumptions. It keeps defeat,
provenance, and evaluation order understandable without adding a default logic
fixpoint or precedence system to P0.

## Consequence

`DEFAULT A -> B` together with `DEFAULT B -> C` does not yield `C` merely from
ordinary support for `A`. A later milestone may introduce a different policy
only through an explicit ADR and conformance changes.
