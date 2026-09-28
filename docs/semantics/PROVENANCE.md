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

P0.10 justification nodes expose the proposition, polarity, support kind,
direct origin when applicable, rule/premise links when applicable, and whether
a default support is defeated. `queried_at_revision` identifies query context;
an unavailable originating revision is represented explicitly as absent rather
than inferred.

Trigger-created persistent direct support additionally records its trigger rule
ID and the deterministically ordered premise support IDs that matched the
frozen snapshot. This metadata is historical: later premise retraction does not
erase it. `why_in_world(world, proposition)` resolves each persistent support's
first committed revision while keeping evaluated DERIVE/DEFAULT supports
explicitly without an originating revision.

If multiple trigger matches produce one identical output, P0 retains the
lexicographically smallest premise-ID path; this deliberate P0 limitation is
recorded in [ADR 0009](../adr/0009-persistent-trigger-causal-provenance.md).

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
