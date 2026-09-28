# WorldPatch Semantics v0

## Purpose
A WorldPatch is the only standard path for persistent semantic mutation.

## Required properties
- explicit operations;
- full validation before commit;
- atomic all-or-nothing commit;
- deterministic result;
- provenance recorded for the commit;
- immutable revision generated on success.

## P0 operation model
P0 should minimally support operations equivalent to:
- add direct positive support;
- add direct negative support;
- remove a specific direct support;
- optionally define/remove relation/rule records when their schema is introduced in the same milestone.

The exact API shape may evolve, but patch semantics must remain atomic.

## Validation layers
### Structural validation
Examples:
- referenced relation exists;
- arity is correct;
- argument types are well formed;
- support/relation/rule IDs are valid.

### Semantic validation
P0 semantic validation is intentionally narrow. Contradiction is not automatically invalid.

Examples of invalidity:
- malformed relation application;
- illegal reference to nonexistent schema;
- patch operation against a missing target support when operation requires exact identity.

## Contradiction is not transaction failure
A patch may validly produce:
```text
+P
-P
```
and therefore CONFLICT.

This is a semantic outcome, not an invalid patch.

## Revision
Successful commit creates a revision containing at least:
- revision ID;
- parent revision ID;
- canonical patch representation;
- provenance metadata;
- deterministic ordering metadata as needed.

## Dry run
The eventual LLM/UI layer should be able to validate and inspect a patch without committing it. P0 should avoid architecture that makes dry-run impossible.
