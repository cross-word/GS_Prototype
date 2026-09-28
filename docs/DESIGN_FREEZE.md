# Design Freeze — P0 Entry Point

This file records the decisions considered stable enough to begin implementation. "Frozen" means implementation should not reinterpret them silently; it does not mean they can never change.

## Frozen for P0
1. The project is a world-definition simulation, not an LLM-authored narrative simulator.
2. The semantic runtime is authoritative; LLM integration comes later.
3. Meta-Kernel primitives are limited to the domain-neutral set documented in `semantics/META_KERNEL.md`.
4. Entity, Concept, State, Event, Time, Space, Cause, and related world concepts are libraries above the Kernel.
5. Proposition truth is support-based and open-world.
6. Positive and negative support are independent; effective status is UNKNOWN / TRUE_ONLY / FALSE_ONLY / CONFLICT.
7. Contradictions are preserved without logical explosion.
8. Assertion storage is conceptually modeled as Proposition + Support + Provenance rather than a single truth-valued fact row.
9. DERIVE, DEFAULT, and TRIGGER are distinct semantics.
10. DERIVE uses truth maintenance and may have multiple justification paths.
11. DEFAULT support is defeasible; conflicting non-default support defeats a contrary default in v0.
12. TRIGGER reads a stable snapshot and produces a patch rather than mutating during condition evaluation.
13. Persistent mutation is atomic through WorldPatch.
14. Every committed mutation creates a revision and provenance record.
15. P0 aims for deterministic behavior.
16. Continuous dynamics, probability, physics, LLM integration, visuals, and rich world libraries are deferred.

## Allowed implementation freedom
Codex/implementers may choose internal data structures, indexes, module/file layout, and API naming when the choice does not alter the frozen semantics.

## Requires design review / ADR
- adding/removing a Meta-Kernel primitive;
- changing the four-state model;
- changing contradiction propagation semantics;
- changing default defeat semantics;
- making world mutation possible outside WorldPatch;
- changing snapshot trigger semantics;
- discarding provenance required for truth maintenance;
- making Entity/Time/State/etc. Kernel primitives.
