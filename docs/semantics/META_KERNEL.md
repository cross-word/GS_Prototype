# Meta-Kernel Specification v0

## Purpose
The Meta-Kernel is a minimal, domain-neutral language/runtime for describing and changing worlds. It should make as few metaphysical assumptions as practical.

It does not define what an entity, state, event, time, cause, location, lifeform, or physical law is.

## Primitive concepts

### 1. ID
Opaque identifier with stable equality inside a world history.

Required property:
```text
same ID => same runtime referent
```

Non-properties:
- does not imply objecthood;
- does not imply persistence in world-level philosophy;
- does not define "same person" or analogous identity claims.

### 2. Value
P0 scalar values:
- Number
- Boolean
- String

Structured values may be added later. Units are not P0 primitives.

### 3. Relation schema
Defines a relation name/ID, arity, and minimal argument well-formedness.

Example conceptual schema:
```text
Relation CanFly(subject: ID)
Relation Health(subject: ID, amount: Number)
```

Semantic properties such as symmetry or transitivity are not automatically Kernel primitives; higher-level rules may express them.

### 4. Proposition
A well-formed relation applied to arguments.

Examples:
```text
CanFly(@pingu)
Health(@rabbit, 10)
ParentOf(@alice, @bob)
```

A proposition has no intrinsic truth bit. Truth status is computed from support.

### 5. Support
A positive or negative justification for a proposition. See `PROPOSITION_SUPPORT.md`.

### 6. Variable / Pattern
Variables are placeholders used in patterns. A pattern matches propositions/support state and produces bindings.

Example:
```text
ParentOf(?x, @bob)
```

### 7. Expression
P0 expressions support minimal deterministic calculation needed by rule guards.

Target P0 operations:
- boolean: AND, OR, NOT (expression negation only)
- equality: ==, !=
- comparison: <, <=, >, >=
- arithmetic: +, -, *, /

Explicit negative proposition support is not represented by boolean NOT.

### 8. Rule
P0 rule kinds:
- DERIVE
- DEFAULT
- TRIGGER

See `RULE_SEMANTICS.md`.

### 9. WorldPatch
Atomic proposed mutation. See `WORLD_PATCH.md`.

## Intentionally not primitive
The following belong above the Meta-Kernel unless a future ADR proves otherwise:
- Entity
- Concept
- Property
- State
- Event
- Transition
- Time
- Space
- Position
- Cause
- Action
- Quantity / unit
- Object
- Life / Death
- Physics

## Kernel vs runtime infrastructure
The following are required implementation infrastructure but are not player-world concepts:
- support/proposition indexes;
- transaction engine;
- rule scheduler;
- provenance store;
- revision history;
- persistence adapter;
- resource limits.
