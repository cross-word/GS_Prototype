# S12 — Atomic Patch

**Milestone:** P0

## Player intent
Create concept-like records for a new creature and several related definitions in one patch.

## Patch fixture
The patch contains multiple valid operations and one structurally invalid proposition, such as an argument with the wrong value type for its relation schema.

## Expect
- Validation fails.
- No operation is committed.
- Revision history is unchanged.
- A structured validation error identifies the invalid operation.

## Purpose
Validates all-or-nothing mutation.
