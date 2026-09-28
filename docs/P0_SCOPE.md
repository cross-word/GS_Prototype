# P0 Scope — Semantic Kernel Reference Implementation

## Goal
Prove that the proposed semantic model is coherent, deterministic, explainable, and implementable before introducing simulation-heavy or visual systems.

P0 is complete when the designated P0 conformance scenarios are executable and pass.

## In scope
### P0.1 — IDs, values, relations, propositions
- Opaque IDs.
- Scalar values: number, boolean, string.
- Relation schemas with arity and argument-type validation.
- Propositions as relation + arguments.

### P0.2 — Supports and four-state status
- Positive and negative supports.
- UNKNOWN / TRUE_ONLY / FALSE_ONLY / CONFLICT.
- Direct support provenance.

### P0.3 — Pattern matching
- Variables.
- Pattern matching over propositions/support status.
- Conjunctive matching sufficient for P0 rules.

### P0.4 — DERIVE
- Monotonic derivation.
- Derived support linked to its premises and rule.
- Duplicate suppression.

### P0.5 — Truth maintenance
- Multiple derivations for one proposition.
- Removal of one support path does not retract conclusions still supported by another path.
- Retraction propagates through invalidated justifications.

### P0.6 — DEFAULT
- Defeasible positive/negative support.
- Explicit/ordinary support defeats conflicting default support.
- Defeated defaults remain explainable in provenance.

### P0.7 — WorldPatch
- Validate all operations before commit.
- All-or-nothing atomicity.
- Revision creation.
- Direct support add/remove operations.

### P0.8 — TRIGGER
- Evaluate trigger conditions against one committed snapshot.
- Trigger output is a patch proposal.
- No mid-phase mutation visibility.
- Deterministic ordering/merge for non-conflicting patches.

### P0.9 — Provenance
- Every support records origin.
- Derived support records rule and premise supports.
- Every commit records parent revision and patch.
- "Why?" query can return a machine-readable justification graph.

### P0.10 — Runtime integration and hardening
- Frozen evaluated semantic snapshots and one runtime orchestration API.
- Triggers observe active derived/default support and commit deterministic patches.
- Canonical numeric semantic identity and immutable commit records.
- Truthful why-query metadata, non-chaining DEFAULT policy, and typed rule guards.

## Explicitly out of scope
- Continuous-time/rate systems.
- World-level Time/Space/Event/State libraries.
- Physics or game-engine integration.
- Probability and RNG.
- Aggregates.
- LLM integration.
- UI.
- Network/multiplayer.
- Generated assets.
- Performance optimization beyond what is needed for tests.

## P0 quality bar
- Deterministic tests.
- No semantic behavior hidden in incidental container ordering.
- Pure semantic core separated from persistence/UI concerns.
- Clear errors for malformed propositions and invalid patches.
- All semantic behavior justified by specification or ADR.
