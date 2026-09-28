# S15 — No Death

**Milestone:** Deferred (P3/P5)

## Player request
"Make a world without death."

## Expected interaction
The system must not encode this as a magical built-in `Death = false` switch unless the active world model explicitly defines one.

Instead, the compiler should inspect how the selected preset operationalizes death (e.g. health threshold, alive state, metabolism, consciousness, decay, agency) and propose an explicit WorldPatch.

Possible clarification:
"Should metabolism and bodily decay continue while consciousness remains?"

## Purpose
Tests the product thesis: high-level philosophical language must be compiled into operational world semantics.
