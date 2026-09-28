# P0.10 — Semantic Runtime Integration & Hardening

## Purpose

This milestone closes the gap between the individually implemented P0 components and a coherent, integrated semantic runtime.

P0.1–P0.9 implemented the major building blocks:

- IDs, values, relation schemas, propositions
- positive/negative supports and four-state status
- pattern matching
- DERIVE rules
- truth maintenance
- DEFAULT rules
- atomic WorldPatch commits
- TRIGGER rules
- justification graphs

Those components currently work mostly as independent layers. P0.10 must connect them into one deterministic semantic evaluation pipeline while hardening provenance, trigger semantics, revision identity, and missing conformance coverage.

This milestone MUST NOT introduce Standard World Model concepts such as Entity, State, Event, Time, Space, Physics, Life, Death, or gameplay-specific ontology.

---

## Read Before Editing

Read these files before implementation:

1. `AGENTS.md`
2. `docs/DESIGN_FREEZE.md`
3. `docs/P0_SCOPE.md`
4. `docs/ARCHITECTURE.md`
5. `docs/semantics/META_KERNEL.md`
6. `docs/semantics/PROPOSITION_SUPPORT.md`
7. `docs/semantics/RULE_SEMANTICS.md`
8. `docs/semantics/WORLD_PATCH.md`
9. `docs/semantics/PROVENANCE.md`
10. `docs/scenarios/S08_SIMULTANEOUS_DAMAGE.md`
11. `docs/scenarios/S13_WHY_QUERY.md`

Inspect the current implementations in:

- `src/worldkernel/model.py`
- `src/worldkernel/support.py`
- `src/worldkernel/rules.py`
- `src/worldkernel/defaults.py`
- `src/worldkernel/maintenance.py`
- `src/worldkernel/world.py`
- `src/worldkernel/triggers.py`
- `src/worldkernel/provenance.py`
- `src/worldkernel/pattern.py`

Do not silently reinterpret an existing ADR or frozen semantic decision.

---

# 1. Architectural Goal

After P0.10, the semantic runtime should expose a coherent flow conceptually equivalent to:

```text
Committed World Revision
        │
        ▼
Direct Supports
        │
        ▼
DERIVE closure
        │
        ▼
DEFAULT candidate generation
        │
        ▼
Default defeat / effective support view
        │
        ▼
Semantic Snapshot
        │
        ▼
TRIGGER evaluation against that frozen snapshot
        │
        ▼
WorldPatch proposal
        │
        ▼
Validation
        │
        ▼
Atomic Commit
        │
        ▼
Next World Revision
```

The authoritative committed world state may continue to store only persistent/direct supports if that design remains clean.

Derived/default supports do **not** need to become persistent world mutations merely to make them visible to trigger evaluation.

The important requirement is that one integrated runtime can compute the semantic view of a committed revision and pass that exact stable view into trigger evaluation.

---

# 2. Required Deliverable: SemanticSnapshot

Introduce a domain-neutral snapshot abstraction, tentatively named:

```text
SemanticSnapshot
```

Equivalent naming is acceptable if justified, but do not use Standard World Model terms such as `State`, `Event`, or `Entity`.

A snapshot should expose enough information to represent the evaluated semantic view of one committed revision.

Recommended conceptual contents:

```text
SemanticSnapshot
    revision_id
    direct_supports
    derived_supports
    default_supports
    supports
```

It MAY additionally provide deterministic query helpers such as:

```text
supports_for(proposition)
effective_status(proposition)
```

Do not precompute all possible propositions merely to populate an `effective_statuses` dictionary.

The snapshot should represent a frozen evaluated view and must not mutate while trigger conditions are being evaluated.

---

# 3. Required Deliverable: SemanticRuntime / Evaluation Orchestrator

Introduce one orchestration API responsible for semantic evaluation.

Tentative shape:

```python
runtime = SemanticRuntime(
    derive_rules=...,
    default_rules=...,
    trigger_rules=...,
)

snapshot = runtime.evaluate(world)
updated_world = runtime.run_trigger_phase(world)
```

Exact API names are implementation freedom.

The runtime MUST:

1. start from the committed revision's persistent/direct supports;
2. compute DERIVE closure;
3. compute DEFAULT candidates after ordinary DERIVE closure;
4. preserve defeated default supports for provenance;
5. expose the resulting semantic snapshot;
6. evaluate triggers against that frozen semantic snapshot;
7. produce one deterministic patch proposal for the phase;
8. validate and atomically commit that patch;
9. leave the original immutable `World` unchanged.

Do not duplicate semantic logic already implemented in `derive_closure`, `evaluate_defaults`, `effective_status`, etc. Prefer composition/refactoring.

---

# 4. Trigger Evaluation Must See Evaluated Semantics

Current trigger evaluation uses committed direct supports only.

P0.10 must ensure that triggers can observe active semantic support produced by DERIVE and DEFAULT evaluation where appropriate.

Required conformance example:

```text
+Penguin(Pingu)

DERIVE:
    +Penguin(?x)
    ->
    +Bird(?x)

TRIGGER:
    +Bird(?x)
    ->
    ADD +ObservedBird(?x)
```

Expected result:

```text
+ObservedBird(Pingu)
```

after the trigger phase commits.

The trigger did not require `+Bird(Pingu)` to exist as a persistent direct support; it observed the evaluated semantic snapshot.

---

# 5. Trigger Snapshot Isolation

Implement the P0 conformance scenario:

```text
S08_SIMULTANEOUS_DAMAGE
```

The semantic requirement is not a particular health arithmetic language.

The test MUST demonstrate:

- two or more triggers are evaluated from the same frozen snapshot;
- no trigger sees a support produced by another trigger in that same phase;
- outputs are gathered before mutation;
- the final patch is deterministic;
- one trigger's incidental iteration order cannot affect another trigger's applicability.

A minimal domain-neutral fixture is preferred.

For example:

```text
+Source(A)

Trigger 1:
    Source(A)
    ->
    ADD Intermediate(A)

Trigger 2:
    Intermediate(A)
    ->
    ADD Final(A)
```

During the **same** trigger phase:

```text
Intermediate(A) is added
Final(A) is NOT added
```

because Trigger 2 must not observe Trigger 1's output until a later phase.

A second trigger phase may then produce `Final(A)`.

---

# 6. Trigger Output Deduplication

Current trigger support identity can collide when multiple bindings produce the same semantic output.

Example:

```text
Friend(Alice, Bob)
Friend(Alice, Carol)

TRIGGER:
    Friend(?x, ?y)
    ->
    Alert(?x)
```

Both matches produce:

```text
Alert(Alice)
```

The trigger phase MUST NOT fail because it generated two identical add operations with the same support identity.

Before commit:

- semantically identical trigger outputs must be deterministically deduplicated;
- ordering must remain deterministic;
- distinct outputs must remain distinct.

Add a focused regression test.

---

# 7. Repeated Trigger Firings

Define and document the P0 behavior when the same trigger produces the same output in a later phase.

P0.10 should choose the simplest deterministic behavior consistent with persistent support IDs.

Recommended P0 policy:

```text
If an identical active trigger-produced support already exists,
the later identical output is treated as an idempotent no-op.
```

Do not create a new event/history ontology to solve this.

If another policy is selected, record it in an ADR.

Add a regression test.

---

# 8. Revision Identity Must Include Semantic Content

Current revision identity must not be determined only by parent revision, patch ID, and support IDs.

Two different semantic commits must not receive the same revision ID merely because their support IDs happen to be identical.

Revision identity must use a deterministic canonical representation containing sufficient semantic content.

At minimum, committed support identity should account for:

```text
support ID
relation identity/schema
arguments
polarity
origin
```

Alternatively, hash the canonical validated patch plus parent revision if that gives a stronger and simpler invariant.

Add a regression test proving that two semantically different child worlds from the same parent cannot receive the same revision ID merely by reusing the same patch/support identifiers.

Do not use Python's process-randomized `hash()`.

---

# 9. Commit Provenance

A revision currently retains a `patch_id`, but P0 provenance requires enough information to reconstruct and explain the commit.

Extend revision/commit history so a successful commit preserves a canonical immutable commit record.

Recommended conceptual model:

```text
Revision
    revision_id
    parent_revision_id
    commit_record
    persistent_supports

CommitRecord
    patch_id
    source
    canonical_operations
```

Equivalent design is acceptable.

Required properties:

- original patch source is retained;
- canonical committed operations are retained;
- parent-child revision lineage is retained;
- commit records are immutable;
- dry-run does not create a revision or commit record;
- failed patches create no commit provenance.

A caller must be able to inspect a revision and answer:

```text
Which patch created this revision?
What operations were committed?
What was the source category?
What was the parent revision?
```

---

# 10. Support Provenance Hardening

`why()` currently returns a useful support DAG but lacks several required semantic fields.

Extend machine-readable justification nodes to expose at least:

```text
support_id
proposition
polarity
support_kind
direct origin, when applicable
rule_id, when applicable
premise_support_ids
default defeated status, when applicable
```

Revision metadata must be truthful.

Do **not** assign one caller-provided revision ID to every node as though every support originated in that revision.

Distinguish, where useful:

```text
queried_at_revision
originating_revision
```

If originating revision cannot yet be known for derived/default ephemeral supports, represent that explicitly rather than fabricating provenance.

Update `docs/semantics/PROVENANCE.md` if the exact P0 representation needs clarification.

---

# 11. Why-Query Requirements

Update S13 and provenance unit tests.

For a chain such as:

```text
+Penguin(Pingu)

Penguin -> Bird
Bird -> Animal
```

a why-query for `Animal(Pingu)` must allow a future consumer to reconstruct:

```text
Animal(Pingu)
    ← Bird -> Animal
    ← Bird(Pingu)
    ← Penguin -> Bird
    ← Penguin(Pingu)
```

The graph must expose:

- final derived support;
- each rule ID;
- intermediate propositions;
- polarities;
- premise edges;
- original direct support and origin;
- all alternative justification paths when more than one exists.

Natural-language explanation remains out of scope.

---

# 12. Minimal Expression / Guard Semantics

The Meta-Kernel specification currently lists minimal expressions, while the implementation has no explicit expression/guard layer.

P0.10 should resolve this inconsistency.

Preferred solution: implement a deliberately small, typed, deterministic expression AST sufficient for rule guards.

Minimum target:

```text
Literal
Variable reference

AND
OR
NOT

==
!=
<
<=
>
>=

+
-
*
/
```

Guard evaluation must:

- use already bound variables;
- reject unbound variable references;
- reject invalid operand types deterministically;
- never use Python `eval`;
- remain domain-neutral.

Example:

```text
Health(?x, ?h)
GUARD ?h <= 0
```

Do not add units, aggregates, probability, functions such as distance, or continuous dynamics in P0.10.

If implementation review finds this addition too invasive for P0.10, the only acceptable alternative is:

1. explicitly remove Expression from the P0 required surface in the specification;
2. move it to P1 in an ADR/document update;
3. do not leave documentation and implementation inconsistent.

Preferred outcome remains a minimal expression/guard implementation.

---

# 13. Numeric Canonicalization

Audit deterministic identity generation involving `NumberValue`.

Python equality can treat:

```text
1 == 1.0
```

as true while textual representations differ.

The kernel must not consider two propositions semantically equal while generating inconsistent deterministic support/revision identities for them.

Choose and document one policy.

Recommended policy:

```text
Numerically equal P0 NumberValue values are semantically equal
and use one canonical deterministic serialization.
```

Examples that should canonicalize consistently:

```text
NumberValue(1)
NumberValue(1.0)
```

If this policy is selected, add tests covering:

- proposition equality;
- derived support identity;
- default support identity;
- canonical revision/patch serialization where numbers participate.

Do not silently rely on `repr()` as the semantic canonicalization format.

---

# 14. DEFAULT Chaining Policy

The current implementation evaluates DEFAULT premises only against ordinary direct/derived supports.

This effectively means:

```text
DEFAULT A -> B
DEFAULT B -> C
```

does not chain through default-derived `B`.

This is a semantic decision and must be explicit.

For P0, adopt:

```text
DEFAULT conclusions DO NOT participate as premises
for generating additional DEFAULT supports.
```

Rationale:

- keeps P0 non-monotonic behavior bounded;
- avoids introducing a defeasible fixed-point algorithm without specification;
- matches current implementation behavior.

Add an ADR or extend the existing DEFAULT semantics ADR/spec.

Add a regression test proving the policy.

Do not implement DEFAULT chaining in P0.10.

---

# 15. Active vs Defeated Defaults in Trigger Matching

Clarify what triggers observe.

Recommended policy:

```text
Triggers observe active semantic support only.
Defeated DEFAULT supports remain available for provenance
but do not satisfy trigger premises.
```

Example:

```text
DEFAULT Bird(x) -> +CanFly(x)
DERIVE Penguin(x) -> -CanFly(x)

TRIGGER +CanFly(x) -> ...
```

For a Penguin whose positive default has been defeated, the positive defeated default must not activate the trigger unless some other active positive non-default support for `CanFly` exists.

Implement and test this policy.

This likely requires the semantic snapshot to distinguish:

```text
all supports
active supports
defeated default supports
```

without deleting provenance.

---

# 16. DERIVE and Conflict Semantics Must Remain Unchanged

Do not accidentally "resolve" explicit contradictions while integrating the runtime.

The following remains required:

```text
+P
-P
=> CONFLICT
```

and both polarities may feed rules that explicitly request those polarities.

Example:

```text
+Mortal(Dragon)
-Mortal(Dragon)

+Mortal(x)  -> +FiniteLife(x)
-Mortal(x)  -> +Eternal(x)
```

Expected:

```text
Mortal(Dragon) = CONFLICT
FiniteLife(Dragon) = TRUE_ONLY
Eternal(Dragon) = TRUE_ONLY
```

No unrelated proposition may be derived merely from the contradiction.

Existing S03 must remain unchanged and pass.

---

# 17. Truth Maintenance Must Remain Support-Path Based

Integration must not collapse derived truth into one boolean/proposition row.

A proposition may have multiple independent justifications.

Removing one premise support removes only downstream supports that depend on that support path.

Existing S04 must remain unchanged and pass.

If semantic snapshots cache derived supports, invalidation behavior must remain logically equivalent to recomputation from the current committed revision.

---

# 18. WorldPatch Atomicity Must Remain Unchanged

All persistent mutations still pass through validated atomic WorldPatch commit.

Required:

```text
validate whole patch
    ↓
all valid -> commit once
any invalid -> commit nothing
```

Contradiction remains a valid semantic result and is not a patch validation failure.

Existing S12 must remain unchanged and pass.

Runtime integration must not introduce direct mutation shortcuts.

---

# 19. Optional but Recommended: Canonical Serialization Utility

Consider adding one small internal canonicalization module used for:

- support deterministic IDs;
- default deterministic IDs;
- trigger deterministic IDs;
- revision IDs;
- future persistence/replay.

Example responsibility:

```text
canonicalize_id(...)
canonicalize_value(...)
canonicalize_relation(...)
canonicalize_proposition(...)
canonicalize_support(...)
canonicalize_patch(...)
```

Do not introduce a large serialization framework.

The goal is to stop semantic identity from depending on incidental `repr()` behavior.

If added, cover it with focused unit tests.

---

# 20. Required Conformance Tests

The following existing P0 conformance scenarios must pass after P0.10:

```text
S01_UNKNOWN_CREATURE
S02_BIRD_PENGUIN
S03_CONTRADICTORY_DRAGON
S04_MULTIPLE_SUPPORTS
S05_GLASS_BREAK
S12_ATOMIC_PATCH
S13_WHY_QUERY
```

Implement and pass:

```text
S08_SIMULTANEOUS_DAMAGE
```

Additionally add integration/regression coverage for:

```text
I01 derived support visible to trigger
I02 defeated default not visible to trigger
I03 duplicate trigger output deduplicated
I04 repeated identical trigger output is idempotent
I05 semantic revision identity collision prevention
I06 commit record preserves canonical patch/source
I07 why-query includes proposition/polarity/origin
I08 numeric canonicalization
I09 DEFAULT chaining is intentionally disabled
I10 runtime evaluation is deterministic under reordered input collections
```

Test names do not have to use these exact identifiers.

---

# 21. Determinism Requirements

Equivalent semantic input must produce equivalent output independent of:

- Python set/dict incidental iteration order;
- input rule ordering where rule ordering is not semantically meaningful;
- input support ordering where support ordering is not semantically meaningful.

Use explicit stable sorting/canonicalization where needed.

Tests should deliberately reverse/shuffle logically equivalent input tuples where practical and compare results.

Do not introduce randomness.

---

# 22. Resource Limits

Keep existing DERIVE iteration bounds.

P0.10 does not need a general scheduler/resource-budget framework.

However:

- integrated runtime must surface derivation-limit failures clearly;
- failure must not partially mutate the committed world;
- trigger phase must not commit if semantic evaluation required for that phase fails.

Add a focused test if integration makes this behavior non-obvious.

---

# 23. Public API

Update `src/worldkernel/__init__.py` only with stable P0.10 public abstractions.

Likely public candidates:

```text
SemanticSnapshot
SemanticRuntime
Expression / guard types if implemented
CommitRecord if intended for inspection
```

Avoid exporting incidental helper functions.

---

# 24. Documentation Updates

Update at least:

```text
README.md
docs/P0_SCOPE.md
docs/DESIGN_FREEZE.md
docs/semantics/RULE_SEMANTICS.md
docs/semantics/PROVENANCE.md
docs/scenarios/README.md
```

Add/update ADRs for:

```text
SemanticSnapshot / integrated runtime
DEFAULT non-chaining policy
Trigger active-support policy
Canonical semantic identity, if a material design decision is introduced
```

README repository status should state that P0.10 integrates and hardens the P0 runtime once complete.

Do not claim P0 is complete until all designated P0 conformance tests pass.

---

# 25. CI

Add a minimal GitHub Actions workflow for the supported Python version(s).

Required CI behavior:

```text
install package with test extras
run full pytest suite
```

Example conceptual command:

```text
python -m pip install -e ".[test]"
python -m pytest
```

Keep CI minimal. No release/publishing workflow is needed.

---

# 26. Non-Goals

Do NOT implement in P0.10:

- Entity / Concept as Kernel primitives
- State / Event / Time / Space
- world-level causality model
- continuous/rate simulation
- physics
- probability/RNG
- aggregates such as COUNT/SUM/AVG
- existential DERIVE creation
- object spawning semantics
- Standard World Model
- presets
- LLM integration
- natural-language explanation
- database persistence
- Godot/Unity/Unreal
- image/3D generation
- NPC behavior
- multiplayer
- self-modifying Meta-Kernel rules
- fuzzy logic
- closed-world semantics
- NOT_KNOWN / negation-as-failure
- DEFAULT specificity hierarchy
- DEFAULT chaining

Do not solve future milestones speculatively.

---

# 27. Architectural Invariants

The following are hard requirements.

```text
1. The semantic runtime, not an LLM, remains authoritative.

2. Proposition has no intrinsic truth field.

3. Truth remains support-based.

4. Unknown remains distinct from explicit negative support.

5. Contradiction remains representable and non-explosive.

6. Persistent mutation occurs only through atomic WorldPatch.

7. DERIVE and TRIGGER remain distinct.

8. Defeated defaults remain available for provenance.

9. Runtime execution order is not world-level Time.

10. Entity, State, Event, Time, Space, Cause, Physics, etc.
    remain outside the Meta-Kernel.

11. Do not introduce a new Kernel primitive without an ADR.
```

If any requested change appears to require violating one of these invariants, stop that part of implementation and document the conflict instead of silently changing semantics.

---

# 28. Suggested Implementation Sequence

Use small commits.

Recommended order:

```text
P0.10a
Canonical semantic serialization + numeric canonicalization

P0.10b
CommitRecord + revision identity/provenance hardening

P0.10c
SemanticSnapshot

P0.10d
SemanticRuntime evaluation pipeline

P0.10e
Trigger reads SemanticSnapshot + active-support filtering

P0.10f
Trigger deduplication + repeated-output idempotence

P0.10g
S08 snapshot isolation conformance

P0.10h
Provenance / why-query hardening

P0.10i
DEFAULT non-chaining ADR + tests

P0.10j
Minimal expressions/guards

P0.10k
GitHub Actions CI + full P0 regression
```

The exact split may change if a smaller dependency-respecting sequence is cleaner.

Do not combine the entire milestone into one opaque commit.

---

# 29. Completion Criteria

P0.10 is complete only when all of the following are true:

- [ ] A coherent `SemanticSnapshot`-like evaluated view exists.
- [ ] A runtime/orchestrator connects DERIVE → DEFAULT → effective view → TRIGGER.
- [ ] Triggers can observe active derived semantic support.
- [ ] Defeated DEFAULT support cannot activate triggers.
- [ ] Trigger evaluation is snapshot-isolated.
- [ ] S08 exists as an executable conformance test and passes.
- [ ] Duplicate trigger outputs are deterministic and safe.
- [ ] Repeated identical trigger outputs have explicit deterministic semantics.
- [ ] Revision identity includes semantic content and collision regression tests pass.
- [ ] Revision history retains immutable canonical commit provenance.
- [ ] `why()` exposes proposition, polarity, origin/rule, premises, and honest revision context.
- [ ] DEFAULT chaining policy is documented and tested.
- [ ] Numeric canonicalization is deterministic and tested.
- [ ] Expression/guard documentation and implementation are consistent.
- [ ] Existing S01/S02/S03/S04/S05/S12/S13 tests still pass.
- [ ] New P0.10 integration/regression tests pass.
- [ ] Full pytest suite passes.
- [ ] GitHub Actions runs the full pytest suite.
- [ ] No Standard World Model concept was introduced into the Meta-Kernel.
- [ ] Documentation accurately reflects the resulting runtime.

---

# 30. Required Final Report From Codex

When implementation is complete, report:

1. files changed;
2. architectural changes made;
3. ADRs added/updated;
4. tests added;
5. exact full-suite test command and result;
6. CI workflow added and its scope;
7. any specification ambiguity encountered;
8. any requirement intentionally deferred;
9. confirmation that no Kernel boundary invariant was violated.

Do not report the milestone as complete if a designated conformance scenario is missing or skipped.
