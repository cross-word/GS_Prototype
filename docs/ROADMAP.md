# Roadmap

## P0 — Semantic Kernel
Reference implementation of propositions, supports, rules, patches, provenance, and conformance tests.

## P1 — Standard World Model
Introduce optional libraries for:
- Entity / Concept / InstanceOf / SubtypeOf
- Property conventions
- State
- Event / Transition
- basic Time abstraction
- basic Space/Position abstraction
- Cause / Action
- Quantity and units

These remain libraries, not Meta-Kernel primitives.

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
