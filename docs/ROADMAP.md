# Roadmap

## P0 — Semantic Kernel
Reference implementation of propositions, supports, rules, patches, provenance, and conformance tests.

## P1 — Standard World Model
Implement the static/deductive Standard World Model defined by
[`P1_STANDARD_WORLD_MODEL.md`](P1_STANDARD_WORLD_MODEL.md):
- Concept / Entity / Label / InstanceOf / SubtypeOf;
- typed, multi-valued attributes;
- world-defined binary relations;
- builders, evaluated-snapshot queries, and diagnostics.

These remain libraries, not Meta-Kernel primitives.

**Status: COMPLETE.** State, Event, Time, Space, Cause, Action, Quantity,
and units are explicitly deferred to separately designed future milestones.

## P2 — Simulation Runtime
Add:
- event queue;
- simulation stepping;
- continuous/rate rules;
- resource budgets;
- deterministic RNG;
- basic aggregate expressions;
- world forks and replay.

## P3 — Natural-Language World Compiler
Add an LLM front-end:
- retrieve relevant definitions;
- compile player requests to typed WorldPatch proposals;
- validation and repair loop;
- impact preview;
- ambiguity handling;
- "why?" explanations from provenance.

## P4 — Minimal Game Client
Add a simple 2D/3D sandbox with primitive visual placeholders and free camera. Validate whether defining, observing, and debugging worlds is enjoyable.

## P5 — Domain Packages and Presets
Add Basic World and limited counterfactual presets. Modern Earth should be treated as an explicit approximation, not a claim of complete reality simulation.

## P6 — Generative Representation
Add semantic-to-visual generation, cached assets, semantic/visual separation, part-aware representation, and optional procedural animation.

## P7 — Complex Agents / Society
Add high-level NPC goals, utility/GOAP behavior, social structures, and selected world-model modules without making LLMs authoritative per-frame agents.
