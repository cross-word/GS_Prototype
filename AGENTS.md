# AGENTS.md

## Purpose
This repository implements the semantic foundation for a world-definition simulation game. The player describes worlds in natural language; an LLM may later translate those descriptions into validated world changes. The semantic runtime, not the LLM, is authoritative.

## Architectural invariants
1. The Meta-Kernel MUST NOT depend on the Standard World Model, simulation, rendering, asset generation, or LLM code.
2. The Meta-Kernel MUST NOT hard-code gameplay concepts such as Entity, Concept, State, Event, Time, Space, Cause, Physics, Life, Death, Magic, Society, or Economy.
3. World truth is represented as propositions with positive and/or negative support. Unknown is distinct from explicit negative support.
4. Contradictions are preserved. They MUST NOT trigger classical explosion or allow arbitrary conclusions.
5. Derived conclusions MUST retain justification/provenance sufficient to explain why they exist and to retract them when their support disappears.
6. All persistent world mutations MUST occur through validated atomic WorldPatch commits.
7. Logical derivation and state-changing triggers are different semantics and MUST remain separate.
8. Runtime execution order is not the same thing as world-level time. Internal ticks MUST NOT be exposed as the definition of Time.
9. Runtime IDs are opaque implementation identities and MUST NOT be treated as world-level philosophical identity.
10. Do not introduce a new Meta-Kernel primitive without an ADR.

## P0 implementation target
P0 is a semantic kernel reference implementation. No game UI, physics, 3D generation, NPC agent system, or LLM integration belongs in P0.

Required P0 capabilities:
- Opaque IDs and scalar values.
- Relation schemas and well-formed propositions.
- Positive/negative supports.
- Four effective statuses: UNKNOWN, TRUE_ONLY, FALSE_ONLY, CONFLICT.
- Pattern matching and variables.
- DERIVE rules.
- Multiple justifications and truth maintenance.
- DEFAULT rules with defeasible support.
- Atomic WorldPatch validation/commit.
- TRIGGER rules evaluated against snapshots and producing patches.
- Provenance and deterministic revision history.
- Conformance scenarios marked P0 in `docs/scenarios/README.md`.

## Non-goals for P0
Do not implement unless a later milestone explicitly requests it:
- World-level Time, Space, State, Event, Entity, Concept, Property, Cause, Quantity.
- Continuous dynamics.
- Physics.
- Randomness/probability.
- Aggregates such as COUNT/SUM.
- Existential rule creation except explicit patch-level FRESH_ID when introduced.
- Self-modifying Meta-Kernel semantics.
- LLM calls.
- Godot/Unity/Unreal integration.
- Generative images, 3D, rigging, animation.
- Multiplayer/network replication.

## Change discipline
- Read the relevant semantic specification and ADRs before editing code.
- Prefer the smallest change that satisfies the current milestone.
- Add or update tests for every semantic change.
- If a requested implementation conflicts with an invariant or ADR, stop and document the conflict instead of silently changing semantics.
- Semantic behavior changes require an ADR or an explicit update to an existing ADR.
- Do not make speculative framework additions for future milestones.

## Test discipline
P0 should be specification-driven.
1. Add/confirm a conformance test.
2. Implement the smallest semantic behavior needed.
3. Run focused tests.
4. Run the full P0 suite.
5. Preserve deterministic output.

## Terminology
Use project terms exactly as defined in `docs/GLOSSARY.md`. In particular, do not use "fact" when the intended meaning is "proposition" or "support".
