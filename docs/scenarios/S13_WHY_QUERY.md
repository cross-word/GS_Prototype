# S13 — Why Query

**Milestone:** P0

## Setup
Construct at least a two-step derivation chain with one direct support, one derived intermediate proposition, and one final derived proposition.

Example:
```text
+Penguin(Pingu)
Penguin -> Bird
Bird -> Animal
```

## Query
Ask for the justification graph of `Animal(Pingu)`.

## Expect
The returned graph identifies:
- the final support;
- the Bird rule;
- the Bird support;
- the Penguin rule;
- the original direct support;
- originating revision IDs.

## Purpose
Ensures provenance is complete enough for future natural-language "why?" explanations.
