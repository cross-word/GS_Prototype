# Rule Semantics v0

## Principle
Not every `A -> B` has the same meaning. Logical implication and state mutation are separate semantics.

## DERIVE
A DERIVE rule creates derived support while its premises are supported.

Example:
```text
DERIVE
  Bird(?x)
THEN
  +Animal(?x)
```

Properties:
- truth-maintained;
- may reach closure through repeated derivation;
- removing all justification paths removes the derived support;
- duplicate derivations are deduplicated by justification identity or equivalent canonicalization.

## DEFAULT
A DEFAULT rule proposes defeasible support.

Example:
```text
DEFAULT
  Bird(?x)
THEN
  +CanFly(?x)
```

P0 defeat rule:
- conflicting active non-default support defeats a contrary default support;
- default-vs-default conflicts are preserved unless a future explicit ordering rule is defined;
- P0 does not infer complex specificity precedence automatically.

A defeated default remains in provenance but is excluded from effective status.

P0 DEFAULT rules are non-chaining: their premises are matched only against
direct and DERIVE support. A DEFAULT conclusion cannot activate another DEFAULT
rule. This policy is fixed by [ADR 0007](../adr/0007-default-non-chaining.md).

## TRIGGER
A TRIGGER rule observes a committed snapshot and proposes a persistent WorldPatch.

Example:
```text
TRIGGER
  ON Collision(?x, Ground)
  IF Glass(?x)
THEN PATCH
  ADD +Broken(?x)
```

Properties:
- conditions are evaluated against one snapshot;
- generated mutations are not visible to other rules in the same evaluation phase unless a later phase explicitly begins;
- output is validated as a patch before commit;
- after commit, the resulting support persists according to patch semantics, even if the triggering condition later disappears.
- persistent results retain structured trigger rule/premise provenance, but are
  not DERIVE supports.

## Snapshot semantics
Within one trigger phase:
1. Freeze the committed semantic snapshot.
2. Find all applicable triggers.
3. Build their patch proposals.
4. Validate/merge according to deterministic conflict policy.
5. Commit atomically as one or more explicitly ordered revisions.

P0 must not expose incidental iteration order as world semantics.

## Derivation closure
DERIVE rules run until no new active derived supports are produced or until a resource limit is reached.

Cycles such as:
```text
A -> B
B -> A
```
terminate through duplicate support/proposition detection.

Unbounded generators are not valid DERIVE behavior in P0; fresh object creation belongs to mutation/trigger semantics.

## Guards and expressions

A rule MAY have one guard, evaluated after its premises have bound variables and
before it produces a conclusion or patch operation. P0.10 expressions are a
small typed AST: literals, bound-variable references, `AND`/`OR`/`NOT`,
equality and ordering comparisons, and numeric `+`, `-`, `*`, `/`.

Guards must evaluate to Boolean. Referencing an unbound variable, applying an
operator to invalid operand types, or division by zero is a deterministic
validation/evaluation error. The kernel never evaluates host-language source
text. Expressions add no units, aggregates, functions, probability, or
continuous dynamics.

## Evaluation phases
Conceptual P0 order:
```text
base/direct supports
  ↓
DERIVE closure
  ↓
DEFAULT candidate generation and defeat resolution
  ↓
effective semantic view
  ↓
TRIGGER snapshot evaluation
  ↓
WorldPatch commit
```

## Deferred rule semantics
Not P0:
- continuous/rate rules;
- probabilistic rules;
- NOT_KNOWN premises;
- aggregates;
- existential generation in DERIVE;
- self-modifying Kernel rules;
- automatic specificity hierarchies;
- fuzzy truth.
