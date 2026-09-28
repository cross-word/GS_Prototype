# Provenance Specification v0

## Purpose
Explainability is part of the game, not only a debugging feature.

The runtime must be able to answer why a proposition has its current support and how a persistent mutation entered world history.

## Support provenance
Each support should identify:
- support ID;
- proposition ID/value;
- polarity;
- support kind (direct, derived, default-derived);
- originating revision;
- originating patch or rule;
- premise support IDs / justification edges;
- active/removed/defeated state where applicable.

## Commit provenance
Each committed patch should identify:
- revision;
- parent revision;
- patch ID;
- source category (player, trigger, import, later LLM compiler, etc.);
- operations;
- validation result;
- deterministic metadata needed for replay.

## Why-query
P0 should expose a machine-readable query capable of producing a justification graph for a selected support or proposition.

Example:
```text
-AnimalAlive(Rabbit512)
  ← DeathRule
  ← Health(Rabbit512, 0)
  ← DamageEvent829
  ← Attack(Fox391, Rabbit512)
```

Natural-language explanation is a future consumer of this graph, not the source of truth.

## Multiple paths
Why-query must preserve alternative support paths instead of arbitrarily selecting one as the only explanation.
