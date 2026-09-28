# P0.11 — Provenance & Semantic Consistency Cleanup

## Purpose

P0.10 successfully integrated the semantic runtime and closed most architectural gaps in the P0 kernel.

The remaining work is intentionally narrow. P0.11 exists to close the last semantic-consistency and provenance gaps before declaring the Meta-Kernel P0 reference implementation complete and moving to P1 Standard World Model work.

This milestone MUST NOT introduce new world concepts or broaden simulation scope.

P0.11 should fix four areas:

1. numeric equality consistency;
2. TriggerRule validation;
3. trigger causal provenance;
4. originating revision provenance where the runtime can know it truthfully.

After this milestone, the project should be able to state that P0 is complete.

---

# 1. Read Before Editing

Read:

1. `AGENTS.md`
2. `docs/DESIGN_FREEZE.md`
3. `docs/P0_SCOPE.md`
4. `docs/P0_10_SEMANTIC_RUNTIME_INTEGRATION_HARDENING.md`
5. `docs/semantics/META_KERNEL.md`
6. `docs/semantics/PROPOSITION_SUPPORT.md`
7. `docs/semantics/RULE_SEMANTICS.md`
8. `docs/semantics/WORLD_PATCH.md`
9. `docs/semantics/PROVENANCE.md`
10. `docs/scenarios/S05_GLASS_BREAK.md`
11. `docs/scenarios/S13_WHY_QUERY.md`

Inspect current implementations:

- `src/worldkernel/canonical.py`
- `src/worldkernel/expressions.py`
- `src/worldkernel/support.py`
- `src/worldkernel/triggers.py`
- `src/worldkernel/runtime.py`
- `src/worldkernel/world.py`
- `src/worldkernel/provenance.py`

Do not change frozen P0 semantics unless an explicit ADR is added.

---

# 2. Scope

P0.11 is a cleanup milestone.

It is NOT:

- a new simulation milestone;
- a persistence milestone;
- a Standard World Model milestone;
- an LLM integration milestone;
- a time/event/physics milestone.

The expected implementation should remain small and surgical.

---

# 3. Numeric Equality Must Be Semantically Consistent

## Problem

P0 currently treats:

```text
NumberValue(1)
NumberValue(1.0)
```

as semantically equal for proposition equality and canonical semantic identity.

ADR 0008 explicitly establishes this policy.

However, expression equality currently uses host-language runtime type identity:

```python
type(left) is type(right) and left == right
```

This causes:

```text
1 == 1.0
```

to evaluate as false in expression guards even though the Meta-Kernel treats the values as semantically equal elsewhere.

This is inconsistent.

## Required behavior

Numeric equality inside expressions MUST follow the same semantic numeric equality policy as `NumberValue`.

Required:

```text
1 == 1.0  -> true
1 != 1.0  -> false
```

while category-incompatible values remain unequal.

Examples:

```text
1 == "1"      -> false
1 == true     -> false
@id == "id"   -> false
```

Do not rely on Python's `bool` being an `int` subclass.

## Ordering

Numeric ordering remains numeric only.

Examples:

```text
1 < 2.0      -> true
2.0 <= 2    -> true
```

Non-numeric ordering must fail deterministically with `InvalidExpressionError`.

## Recommended implementation

Introduce or reuse one semantic equality helper rather than duplicating equality policy.

Conceptually:

```text
semantic_equal(left, right)
```

The helper may remain internal.

If an equality helper becomes an important semantic contract, document it.

## Required regression tests

Add tests for:

```text
E01  NumberValue(1) == NumberValue(1.0)
E02  expression 1 == 1.0 is true
E03  expression 1 != 1.0 is false
E04  expression 1 == "1" is false
E05  expression 1 == true is false
E06  ordering 1 < 2.0 works
```

Also include one guard-level test such as:

```text
Measured(?x, ?n)
GUARD ?n == 1.0

Measured(A, 1)
```

Expected:

```text
rule fires for A
```

---

# 4. TriggerRule Validation Must Match Other Rule Types

## Problem

`DeriveRule` and `DefaultRule` validate structure and variable binding at construction time.

`TriggerRule` currently validates mainly guard-variable binding.

This leaves malformed trigger outputs capable of failing later at execution time with incidental exceptions such as `KeyError`.

That is not acceptable kernel behavior.

## Required TriggerRule validation

At construction time, validate:

```text
rule_id
premises
outputs
guard
output variable binding
```

At minimum:

- `rule_id` must be `OpaqueId`;
- at least one premise must exist;
- every premise must be `SupportPattern`;
- at least one output must exist;
- every output must be `TriggerAdd`;
- output proposition patterns must be valid;
- output polarity must be valid;
- every variable referenced in an output must be bound by a premise;
- every variable referenced by the guard must be bound by a premise.

Malformed trigger rules must fail before runtime execution.

## Structured errors

Use `InvalidRuleError`.

Do not raise raw:

```text
ValueError
KeyError
TypeError
```

for semantic rule validation failures.

Use stable error codes.

Suggested codes:

```text
trigger.invalid_rule_id
trigger.invalid_premises
trigger.invalid_outputs
trigger.unbound_output_variable
trigger.unbound_guard_variable
```

Exact names may differ if consistent with current error conventions.

## Required tests

Add focused tests for:

```text
T01 invalid rule ID
T02 empty premises
T03 invalid premise entry
T04 empty outputs
T05 invalid output entry
T06 unbound output variable
T07 unbound guard variable
```

Valid existing trigger scenarios must continue to pass unchanged.

---

# 5. Trigger-Generated Support Must Preserve Causal Provenance

## Problem

A trigger currently persists its result as a `DirectSupport` with an origin string like:

```text
trigger:break
```

This records the trigger name but loses the causal support path.

For:

```text
+Glass(Cup)
+Collision(Cup, Ground)

TRIGGER Break
  Glass(?x)
  Collision(?x, Ground)
THEN
  +Broken(?x)
```

the runtime should eventually be able to explain:

```text
Broken(Cup)
  <- Trigger Break
  <- Glass(Cup)
  <- Collision(Cup, Ground)
```

Currently the why-graph stops at:

```text
Broken(Cup)
origin = trigger:break
```

This is insufficient for the project's "why did this happen?" design goal.

---

# 6. Do Not Turn Trigger Effects Into DERIVE Supports

Trigger output semantics are persistent mutation.

They must remain distinct from DERIVE.

Do NOT represent trigger-created support as `DerivedSupport` merely to reuse provenance machinery.

That would blur the core distinction:

```text
DERIVE
    truth-maintained logical consequence

TRIGGER
    persistent world mutation caused by a snapshot condition
```

Preserve the rule-kind distinction.

---

# 7. Recommended Provenance Model for Trigger Effects

Introduce explicit provenance metadata for trigger-created persistent support.

Two acceptable design families:

## Option A — New support subtype

For example:

```text
TriggerSupport
    support_id
    proposition
    polarity
    trigger_rule_id
    premise_support_ids
    origin
    originating_revision_id
```

This is acceptable if it remains runtime infrastructure rather than a new player-world primitive.

## Option B — DirectSupport with structured origin/provenance

For example:

```text
DirectSupport
    support_id
    proposition
    polarity
    origin
    provenance
```

where trigger provenance can carry:

```text
trigger_rule_id
premise_support_ids
source_revision_id
```

Either approach is acceptable.

Prefer the smaller change that preserves clean semantics.

---

# 8. Trigger Provenance Must Be Based on the Actual Snapshot Match

When a trigger fires, record the premise support IDs that satisfied the rule.

Example:

```text
Glass(Cup) support = S1
Collision(Cup, Ground) support = S2

Trigger Break
```

Persistent trigger result must preserve:

```text
trigger_rule_id = Break
premise_support_ids = (S1, S2)
```

Use deterministic ordering of premise IDs.

Do not record only proposition values if support-level provenance is available.

This distinction matters when the same proposition has multiple independent support paths.

---

# 9. Trigger Provenance With Multiple Matching Paths

If multiple distinct premise-support combinations produce the same semantic trigger output, current P0 semantics deduplicate identical persistent trigger outputs.

P0.11 must define what provenance survives this deduplication.

Recommended policy:

```text
One persistent trigger support may retain multiple causal justifications.
```

However, if introducing multi-justification trigger support would substantially complicate P0, an acceptable P0 policy is:

```text
Choose one deterministic canonical justification path,
while recording that output deduplication occurred.
```

If the simpler policy is chosen:

- document it explicitly;
- use deterministic canonical selection;
- add an ADR or provenance-spec note;
- do not imply that all causal paths are preserved.

Preferred design remains preserving multiple justifications if it can be done without architectural distortion.

---

# 10. Why-Query Must Follow Trigger Causal Chains

Extend `why()` so trigger-created persistent support can expose its causal chain.

Required example:

```text
+Glass(Cup)
+Collision(Cup, Ground)
TRIGGER Break -> +Broken(Cup)
```

Query:

```text
why(Broken(Cup))
```

Graph must expose enough structure for a future consumer to reconstruct:

```text
Broken(Cup)
  <- Trigger Break
  <- Glass(Cup)
  <- Collision(Cup, Ground)
```

The representation may use support nodes plus trigger metadata.

Natural-language rendering remains out of scope.

---

# 11. Trigger Provenance Must Survive Later Condition Retraction

Scenario S05 remains important.

After:

```text
Collision(Cup, Ground)
```

is removed, `Broken(Cup)` remains supported because it was persistently committed by a trigger.

Its why-query should still preserve the historical trigger cause.

In other words:

```text
premise support inactive now
```

must not erase:

```text
premise caused this persistent trigger result then
```

This is historical provenance, not current truth maintenance.

Do not treat trigger premise retraction like DERIVE premise retraction.

---

# 12. Originating Revision Provenance

## Problem

`JustificationNode` now correctly distinguishes:

```text
queried_at_revision_id
originating_revision_id
```

but currently `originating_revision_id` is always `None`.

The runtime should populate originating revision IDs where the information is truthfully available.

## Required minimum

For persistent supports committed through `WorldPatch`, the runtime should be able to identify the revision in which that support first entered world history.

At minimum support:

```text
DirectSupport added by player patch
Trigger-created persistent support
```

Derived/default supports are evaluated views and do not necessarily have persistent originating revisions.

For ephemeral supports it is acceptable to expose:

```text
originating_revision_id = None
```

if that is semantically correct.

Never fabricate an origin revision.

---

# 13. Revision Provenance Lookup

Add a clean way to resolve:

```text
support_id -> originating revision
```

for persistent support history.

This may be:

- computed by scanning immutable revisions;
- stored in commit provenance;
- indexed by a helper;
- carried structurally in persistent support provenance.

For P0 reference implementation, correctness is more important than optimization.

Do not introduce a database or complex index system.

---

# 14. Removal History

If a persistent support is later removed:

```text
Revision 10: +P added
Revision 15: +P removed
```

why/history tooling should not rewrite its origin as revision 15.

Origin remains revision 10.

P0.11 does not require a full temporal provenance API, but the data model must not make correct removal history impossible.

Optional useful metadata:

```text
originating_revision_id
removed_revision_id
```

Do not overengineer this if not needed by current why-query.

---

# 15. Commit Provenance Must Remain Immutable

Do not weaken P0.10 `CommitRecord`.

The following must remain inspectable:

```text
patch_id
source
canonical operations
parent revision
result revision
```

Trigger causal provenance should reference committed history cleanly rather than modifying old revisions.

---

# 16. Provenance Graph Semantics

`why()` should distinguish at least:

```text
support node
rule relation / rule ID
premise support edges
query revision
origin revision where known
```

The graph does not need a natural-language explanation layer.

It should remain deterministic.

Multiple justification paths for DERIVE must remain preserved.

Default defeat metadata must remain preserved.

Trigger provenance must not break existing DERIVE/DEFAULT behavior.

---

# 17. Direct vs Trigger-Origin Persistent Support

If implementation keeps both as one `DirectSupport` type, the system still needs to distinguish their provenance source.

Conceptual categories may include:

```text
player
import
trigger
future-llm
```

Do not encode semantics by parsing free-form origin strings such as:

```text
"trigger:break"
```

Prefer structured provenance fields for machine-readable behavior.

Human-readable origin labels may remain as auxiliary metadata.

---

# 18. Existing P0 Semantics Must Not Change

The following remain frozen:

```text
open-world semantics
UNKNOWN != FALSE
positive/negative supports independent
CONFLICT allowed
no classical explosion
DERIVE truth maintenance
DEFAULT defeat
DEFAULT non-chaining
TRIGGER persistent mutation
snapshot-isolated trigger evaluation
atomic WorldPatch
deterministic runtime
```

P0.11 is not an opportunity to redesign these decisions.

---

# 19. Required Regression Scenario — Trigger Why

Add a new conformance/integration test.

Suggested scenario:

```text
Glass(Cup)
Collision(Cup, Ground)

TRIGGER Break:
    Glass(?x)
    Collision(?x, Ground)
    ->
    Broken(?x)
```

After one trigger phase:

```text
Broken(Cup) = supported
```

Then query provenance.

Expected graph contains:

```text
Broken(Cup) persistent support
Break trigger rule ID
Glass(Cup) premise support
Collision(Cup, Ground) premise support
originating committed revision for Broken(Cup)
```

Then remove collision support.

Expected:

```text
Broken(Cup) remains supported
why(Broken(Cup)) still retains historical causal premise IDs
```

This should become the canonical trigger-provenance regression.

---

# 20. Required Regression Scenario — Direct Origin Revision

Add a test:

```text
revision 0: empty
revision 1: add +Marker(A)
revision 2: unrelated patch
```

Query provenance for `Marker(A)` at revision 2.

Expected:

```text
queried_at_revision = revision 2
originating_revision = revision 1
```

Do not set origin to revision 2 merely because that is the query context.

---

# 21. Required Regression Scenario — Trigger Origin Revision

Add a test:

```text
revision 1: trigger premises exist
trigger phase commits result -> revision 2
revision 3: unrelated mutation
```

Query trigger-created result at revision 3.

Expected:

```text
queried_at_revision = revision 3
originating_revision = revision 2
```

Trigger causal premise IDs and rule ID remain available.

---

# 22. Optional Provenance Query API

If useful, add a higher-level world-aware provenance entrypoint, conceptually:

```python
why_in_world(world, proposition)
```

or:

```python
runtime.why(world, proposition)
```

This can resolve revision provenance more accurately than a support-only `why()` function.

The existing support-only `why()` may remain if useful.

Do not force historical world knowledge into a pure function that does not receive world history.

A clean API split is preferable to hidden global state.

---

# 23. Required Documentation Updates

Update at least:

```text
README.md
docs/P0_SCOPE.md
docs/DESIGN_FREEZE.md
docs/semantics/PROVENANCE.md
docs/semantics/RULE_SEMANTICS.md
docs/scenarios/README.md
```

Add an ADR if the trigger provenance representation is a material architectural decision.

Suggested ADR:

```text
ADR 0009 — Persistent Trigger Causal Provenance
```

Document:

- trigger effects remain persistent mutation;
- trigger effects are not DERIVE supports;
- causal premise support IDs are retained;
- historical provenance survives premise retraction;
- multi-match deduplication provenance policy.

---

# 24. Required Tests

All existing 70 tests must continue to pass.

Add tests covering at minimum:

```text
C01 expression numeric equality consistency
C02 numeric inequality consistency
C03 mixed-type equality behavior
C04 TriggerRule rejects unbound output variable
C05 TriggerRule rejects malformed structure
C06 trigger-created support records rule ID
C07 trigger-created support records premise support IDs
C08 trigger why-query follows causal premise chain
C09 trigger provenance survives premise removal
C10 direct support originating revision is correct
C11 trigger-created support originating revision is correct
C12 queried revision differs correctly from originating revision
```

If multi-path trigger provenance is preserved:

```text
C13 duplicate semantic trigger output retains all causal justifications
```

If P0 intentionally chooses one canonical path instead:

```text
C13 deterministic canonical causal path selection
```

and document the limitation.

---

# 25. Determinism

All provenance output must be deterministic.

Equivalent input orderings must not change:

```text
support IDs
trigger support identity
selected justification ordering
provenance graph edge ordering
revision attribution
```

Use stable ordering.

Do not use unordered container iteration as semantic behavior.

---

# 26. CI

No new CI framework is required.

Existing GitHub Actions must continue to run:

```text
python -m pip install -e ".[test]"
python -m pytest -q
```

P0.11 is complete only if CI passes on the final commit.

---

# 27. Non-Goals

Do NOT implement:

- Standard World Model
- Entity / Concept / Property libraries
- State / Event / Time / Space
- causality as a player-world ontology
- continuous simulation
- physics
- probability
- aggregates
- NOT_KNOWN
- closed-world relations
- default specificity
- default chaining
- existential generation
- persistence database
- LLM integration
- UI
- natural-language why explanations
- Godot
- graphics
- multiplayer
- optimization work beyond what tests require

Trigger causal provenance is runtime/history metadata, not the introduction of a world-level `Cause` primitive.

---

# 28. Suggested Commit Sequence

Keep work reviewable.

Recommended:

```text
P0.11a
Fix semantic numeric equality in expressions + tests

P0.11b
Harden TriggerRule validation + structured errors

P0.11c
Introduce structured persistent-trigger provenance

P0.11d
Capture trigger premise support IDs at firing time

P0.11e
Extend why-query through trigger causal chains

P0.11f
Resolve persistent-support originating revisions

P0.11g
Add trigger/direct revision provenance regressions

P0.11h
Update ADR/spec/docs and close P0
```

Do not collapse all work into one opaque commit.

---

# 29. Completion Criteria

P0.11 is complete only when:

- [ ] expression numeric equality agrees with NumberValue semantic equality;
- [ ] numeric equality regression tests pass;
- [ ] TriggerRule performs structural validation at construction time;
- [ ] malformed trigger rules fail with `InvalidRuleError`;
- [ ] trigger output variables must be premise-bound;
- [ ] trigger-created persistent support retains structured trigger provenance;
- [ ] trigger provenance includes trigger rule ID;
- [ ] trigger provenance includes actual premise support IDs;
- [ ] why-query can follow trigger-generated causal support chains;
- [ ] trigger provenance remains after trigger premises are later removed;
- [ ] persistent direct support origin revision is recoverable;
- [ ] persistent trigger support origin revision is recoverable;
- [ ] query revision and origin revision are distinguished honestly;
- [ ] existing DERIVE multi-path provenance remains unchanged;
- [ ] DEFAULT defeat provenance remains unchanged;
- [ ] S05 still passes;
- [ ] S13 still passes;
- [ ] all previous P0 conformance tests pass;
- [ ] all new P0.11 regression tests pass;
- [ ] GitHub Actions passes;
- [ ] no Standard World Model concept entered the Meta-Kernel;
- [ ] documentation reflects final behavior.

---

# 30. P0 Closure Condition

After P0.11, if all completion criteria pass, update project status to:

```text
P0 — Semantic Kernel Reference Implementation: COMPLETE
```

Do not begin P1 implementation in the same milestone.

P1 should begin in a separate design/task document after P0 closure.

---

# 31. Required Final Report From Codex

At completion, report:

1. commits created;
2. files changed;
3. exact numeric equality policy implemented;
4. TriggerRule validation behavior;
5. trigger provenance representation chosen;
6. how premise support IDs are captured;
7. multi-match trigger provenance policy;
8. how originating revisions are resolved;
9. why-query changes;
10. tests added;
11. exact full-suite pytest result;
12. GitHub Actions result;
13. documentation/ADR changes;
14. any deferred limitation;
15. confirmation that P0 architectural invariants remain intact.

Do not report P0 as complete if any completion criterion is skipped.
