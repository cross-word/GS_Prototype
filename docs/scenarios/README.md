# Conformance Scenarios

These scenarios convert semantic discussions into observable behavior. They are intended to become executable tests over time.

## P0 scenarios
- `S01_UNKNOWN_CREATURE.md` — unknown vs false.
- `S02_BIRD_PENGUIN.md` — DEFAULT defeat.
- `S03_CONTRADICTORY_DRAGON.md` — contradiction without explosion.
- `S04_MULTIPLE_SUPPORTS.md` — truth maintenance.
- `S05_GLASS_BREAK.md` — DERIVE vs TRIGGER persistence.
- `S08_SIMULTANEOUS_DAMAGE.md` — snapshot semantics.
- `S12_ATOMIC_PATCH.md` — transaction atomicity.
- `S13_WHY_QUERY.md` — provenance.
- `test_trigger_provenance.py` — persistent trigger causal provenance and origin revisions.

The P0.10 regression suite additionally covers derived/default support visible
to triggers, defeated-default exclusion, trigger deduplication/idempotence,
canonical numeric identity, non-chaining defaults, and reordered-input
determinism.

## Deferred but design-relevant scenarios
- `S06_VAMPIRE_SUNLIGHT.md` — continuous/rate rules.
- `S07_RABBIT_FOX.md` — simulation loop.
- `S09_UNBOUNDED_GROWTH.md` — resource semantics.
- `S10_GRAVITY_OVERRIDE.md` — preset layering.
- `S11_MAGIC_COLD_FIRE.md` — defaults vs explicit contradiction.
- `S14_PROBABILISTIC_REPRODUCTION.md` — deterministic RNG.
- `S15_NO_DEATH.md` — operationalizing high-level concepts.

Deferred scenarios should influence architecture but must not cause speculative implementation in P0.
