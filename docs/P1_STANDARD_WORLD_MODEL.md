# P1 — Standard World Model v0

## Purpose

P0 established a domain-neutral semantic Meta-Kernel with opaque IDs, typed values, propositions, support-based four-state semantics, DERIVE / DEFAULT / TRIGGER rules, SemanticSnapshot, atomic WorldPatch mutation, immutable revision history, and provenance.

P1 builds the first practical world-description library **above** that Kernel.

The P1 goal is:

> Provide a reusable object-/concept-oriented Standard World Model that allows a world to define concepts, entities, attributes, and binary relations dynamically without adding new Meta-Kernel primitives.

After P1, the system should represent and query examples such as:

```text
Bear is a Concept.
Animal is a Concept.
Bear is a subtype of Animal.

Bruno is an Entity.
Bruno is an instance of Bear.
Therefore Bruno is also an instance of Animal.

Health is an Attribute.
Bruno has Health = 80.

ParentOf is a world-defined Relation.
Alice ParentOf Bob.
```

P1 is **not** a simulation milestone.


## 1. Architectural Boundary

Dependency direction is fixed:

```text
worldmodel
    ↓
worldkernel
```

The reverse dependency is forbidden.

Recommended package layout:

```text
src/
├── worldkernel/      # P0, authoritative Meta-Kernel
└── worldmodel/
    ├── __init__.py
    ├── vocabulary.py
    ├── ontology.py
    ├── attributes.py
    ├── relations.py
    ├── builders.py
    ├── queries.py
    └── diagnostics.py
```

P1 should require little or no modification to `worldkernel/`.

If implementation appears to require a new Meta-Kernel primitive, stop that change and add an ADR/design note instead of silently changing P0 semantics.


## 2. Central Design Decision

Player/world-defined vocabulary must remain **world data**, not Python/kernel schema proliferation.

When a player defines:

```text
ParentOf
```

P1 should not treat that semantic concept as a newly generated Kernel primitive.

Instead, Standard World Model exposes a small fixed vocabulary:

```text
RelationDef(relation_id)
Related(relation_id, subject_id, object_id)
```

and the world stores:

```text
RelationDef(@parent_of)
Label(@parent_of, "ParentOf")
Related(@parent_of, @alice, @bob)
```

Likewise:

```text
AttributeDef(@health)
Label(@health, "Health")
AttributeNumber(@bruno, @health, 80)
```

This decision is foundational for long-term extensibility.


## 3. P1 Scope

### In scope

```text
Concept
Entity
Label
InstanceOf
SubtypeOf

Attribute definitions
Typed attribute values

World-defined binary relation definitions
Binary relation instances

Builder APIs
Semantic query APIs
Diagnostics
Conformance scenarios
```

### Explicitly out of scope

```text
State
Event
Transition
Time
Ordering
Space
Position
Action
Cause
Physics
Continuous simulation
Probability
NPC behavior
LLM compilation
Graphics
```


## 4. Standard World Model Vocabulary

Implement a small fixed set of P0 `RelationSchema` values, preferably namespaced.

Recommended v0:

```text
Concept(ID)
Entity(ID)

Label(ID, STRING)

InstanceOf(ID, ID)
SubtypeOf(ID, ID)

AttributeDef(ID)

AttributeNumber(ID, ID, NUMBER)
AttributeString(ID, ID, STRING)
AttributeBoolean(ID, ID, BOOLEAN)
AttributeReference(ID, ID, ID)

RelationDef(ID)
Related(ID, ID, ID)
```

Interpretation:

```text
Concept(c)
    c participates as a concept.

Entity(e)
    e participates as an entity.

Label(x,s)
    x has human-readable label s.

InstanceOf(x,c)
    x is an instance of c.

SubtypeOf(a,b)
    concept a is a subtype of b.

AttributeDef(a)
    a is a world-defined attribute.

AttributeNumber/String/Boolean/Reference(x,a,v)
    x has attribute value v under attribute a.

RelationDef(r)
    r is a world-defined binary relation.

Related(r,x,y)
    relation r holds from x to y.
```

Namespaced schema names such as `swm.Concept` are encouraged if they improve collision safety.


## 5. Typed Attribute Relations

P0 `RelationSchema` has fixed argument kinds.

Do not weaken the Kernel type system merely to support one polymorphic:

```text
AttributeValue(ID, ID, VALUE)
```

relation.

Prefer:

```text
AttributeNumber
AttributeString
AttributeBoolean
AttributeReference
```

A higher-level query/helper may expose these as one conceptual attribute API.


## 6. ID and Label Semantics

`OpaqueId` is a runtime reference mechanism. P1 must not reinterpret it as philosophical identity.

Labels are data, not identity.

Valid:

```text
Label(@bear, "Bear")
Label(@bear, "곰")
```

Also valid:

```text
Label(@western_dragon, "Dragon")
Label(@constellation_dragon, "Dragon")
```

Two IDs may share a label and remain distinct.

Automatic natural-language name resolution belongs to a future compiler/interface layer.


## 7. Concept and Entity Are Non-Exclusive Roles

P1 must not impose:

```text
Concept XOR Entity
```

An ID may carry both roles:

```text
Concept(@fire)
Entity(@fire)
```

This supports unusual ontologies without forcing a metaphysical partition.


## 8. Subtype and Instance Inference

P1 defines standard ontology inference using P0 DERIVE.

### Subtype transitivity

```text
SubtypeOf(?a, ?b)
SubtypeOf(?b, ?c)

→ SubtypeOf(?a, ?c)
```

### Instance inheritance

```text
InstanceOf(?x, ?a)
SubtypeOf(?a, ?b)

→ InstanceOf(?x, ?b)
```

Stable rule IDs are required, for example:

```text
swm.rule.subtype_transitivity
swm.rule.instance_inheritance
```

No separate inheritance engine should be created unless a demonstrated requirement cannot be expressed through P0 DERIVE.


## 9. Multiple Inheritance

Multiple inheritance is valid.

```text
SubtypeOf(Bat, Mammal)
SubtypeOf(Bat, FlyingCreature)
InstanceOf(Bruce, Bat)
```

must derive:

```text
InstanceOf(Bruce, Mammal)
InstanceOf(Bruce, FlyingCreature)
```

Do not impose a single-parent hierarchy.


## 10. Subtype Cycles

Example:

```text
SubtypeOf(A, B)
SubtypeOf(B, A)
```

P1 v0 policy:

```text
representable world
+
diagnostic warning
```

rather than commit rejection.

P0 DERIVE closure must terminate deterministically through duplicate suppression.

Add a deterministic diagnostic such as:

```text
subtype_cycle
```

Do not treat subtype cycles as a Kernel error.


## 11. P1 Inherits P0 Open-World and Paraconsistent Semantics

Absence is not false.

```text
no InstanceOf(Kiki, Bird)
```

means UNKNOWN, not explicit negative.

Positive and negative support remain independent.

```text
+InstanceOf(A, Bear)
-InstanceOf(A, Bear)
```

is a conflict, not a fatal exception and not classical explosion.

Do not add a second negation/truth system in `worldmodel`.


## 12. Attribute Semantics

A world defines an attribute as data:

```text
AttributeDef(@health)
Label(@health, "Health")
```

Values are multi-valued by default.

Valid:

```text
AttributeString(Alice, FavoriteColor, "red")
AttributeString(Alice, FavoriteColor, "blue")
```

Also representable:

```text
AttributeNumber(Dragon, Mass, 100)
AttributeNumber(Dragon, Mass, 200)
```

P1 does not automatically decide whether the latter is contradictory.

Functional/cardinality semantics are deferred.

P1 may provide convenience builders such as `set_number_attribute(...)`, but replacement behavior is a helper policy, not a new truth model. Such helpers must only retract appropriate direct supports and must not erase derived/default support.


## 13. World-Defined Binary Relations

World-defined relations are data:

```text
RelationDef(@parent_of)
Label(@parent_of, "ParentOf")
Related(@parent_of, @alice, @bob)
```

P1 v0 supports binary world-defined relations only.

Do not add general n-ary relation semantics in P1.


## 14. Optional Metadata

Optional metadata may be introduced if useful:

```text
AttributeDomain(attribute, concept)
RelationDomain(relation, concept)
RelationRange(relation, concept)
```

If implemented in P1, these are diagnostic metadata, not hard closed-world constraints.

For example:

```text
AttributeDomain(Health, LivingThing)
AttributeNumber(Rock, Health, 20)
```

should not be rejected solely because Rock is not currently known to be a LivingThing.

Open-world semantics must be preserved.


## 15. No Class-Level Attribute Defaults in P1

Do not introduce inherited class-level default attributes in P1 v0.

Example deliberately deferred:

```text
Bird default CanFly=true
Penguin default CanFly=false
```

P0 DEFAULT currently does not define subtype-specific priority, so this would reopen specificity semantics.

P1 v0 supports explicit attribute values only.


## 16. No State / Event / Time / Space

Do not introduce fixed Standard World Model schemas such as:

```text
State(...)
Event(...)
Transition(...)
AtTime(...)
Before(...)
Position(...)
Cause(...)
```

P1 is a static/deductive ontology layer.

A later milestone will separately design change/simulation semantics.


## 17. Vocabulary Module

Recommended responsibility:

```text
worldmodel/vocabulary.py
```

Public constants may include:

```text
CONCEPT
ENTITY
LABEL

INSTANCE_OF
SUBTYPE_OF

ATTRIBUTE_DEF
ATTRIBUTE_NUMBER
ATTRIBUTE_STRING
ATTRIBUTE_BOOLEAN
ATTRIBUTE_REFERENCE

RELATION_DEF
RELATED
```

Vocabulary schemas must have deterministic stable names and argument kinds.


## 18. Ontology Module

Recommended responsibility:

```text
worldmodel/ontology.py
```

Expose an inspectable standard rule set, for example:

```python
standard_ontology_rules() -> tuple[DeriveRule, ...]
```

P1 v0 should contain only the explicitly documented standard inference rules.

Do not hide additional inference behavior.


## 19. Builder APIs

Builders translate high-level Standard World Model edits into atomic `WorldPatch` objects.

Recommended conceptual APIs:

```python
define_concept(...)
create_entity(...)

define_attribute(...)
add_number_attribute(...)
add_string_attribute(...)
add_boolean_attribute(...)
add_reference_attribute(...)

define_relation(...)
add_related(...)
```

Possible forms:

```python
define_concept(
    patch_id,
    concept_id,
    labels=(),
    parent_concepts=(),
    source="..."
) -> WorldPatch
```

```python
create_entity(
    patch_id,
    entity_id,
    labels=(),
    concepts=(),
    source="..."
) -> WorldPatch
```

Requirements:

- builders return patches; they do not mutate `World`;
- all persistent changes still pass through `WorldPatch`;
- one conceptual edit should be atomic;
- support occurrence IDs must obey P0 history uniqueness;
- builders must preserve source/provenance metadata;
- labels must never be used as semantic identity.


## 20. Builder Support Occurrence IDs

P0 forbids historical support-ID reuse.

Therefore builder-generated direct support IDs must be history-safe.

Do not blindly derive a permanent support ID only from semantic proposition content if that prevents legitimate remove-and-readd workflows.

Use either:

- explicit caller-provided support IDs; or
- patch/edit-scoped deterministic occurrence IDs.

Document the strategy and add regression tests for remove/re-add where applicable.


## 21. Semantic Query APIs

Queries operate on an evaluated `SemanticSnapshot`, not raw `world.current.supports`.

Recommended APIs:

```python
labels_of(snapshot, item_id)

concepts_of(snapshot, entity_id)
instances_of(snapshot, concept_id)

direct_subtypes_of(snapshot, concept_id)
all_subtypes_of(snapshot, concept_id)

direct_supertypes_of(snapshot, concept_id)
all_supertypes_of(snapshot, concept_id)

number_attribute_values(...)
string_attribute_values(...)
boolean_attribute_values(...)
reference_attribute_values(...)

related_objects(snapshot, relation_id, subject_id)
relations_between(snapshot, subject_id, object_id)
```

Example:

```text
InstanceOf(Bruno, Bear)
SubtypeOf(Bear, Animal)
```

must allow:

```text
concepts_of(Bruno)
→ Bear, Animal
```

when querying a snapshot evaluated with the P1 standard ontology rules.


## 22. Query Truth Semantics

Query APIs must not hide P0 truth semantics.

Where relevant, distinguish:

```text
positive
negative
unknown
conflict
```

A convenience function may return positively supported values only, but its contract must state that clearly.

Do not treat absence as explicit false.


## 23. Standard Runtime Composition

Provide a convenient way to combine P1 standard inference rules with P0 `SemanticRuntime`.

Examples:

```python
standard_world_rules()
standard_world_runtime(...)
```

or stable exported constants.

Do not fork, copy, or reimplement the P0 runtime.


## 24. Diagnostics

Create a non-authoritative diagnostic layer.

Recommended record:

```text
Diagnostic
    code
    severity
    message
    related_ids
    support_ids
```

Recommended severities:

```text
INFO
WARNING
ERROR
```

Initial candidates:

```text
subtype_cycle
undefined_concept_reference
undefined_attribute_reference
undefined_relation_reference
attribute_domain_not_known
relation_domain_not_known
relation_range_not_known
```

At minimum, implement deterministic subtype-cycle diagnostics.

Diagnostics generally do not change semantic truth and do not replace Kernel validation.


## 25. Validation vs Diagnostics

Distinguish malformed data from unusual but representable worlds.

Structural invalidity such as wrong relation arity should fail through P0 validation.

But:

```text
Concept(A)
Concept(B)
SubtypeOf(A,B)
SubtypeOf(B,A)
```

is representable and should generate a diagnostic rather than commit rejection.


# 26. P1 Conformance Scenarios

## S101 — Basic Concept

Given:

```text
Concept(Animal)
Label(Animal, "Animal")
```

Expect Concept support and label query `"Animal"`.

## S102 — Entity Instance

```text
Concept(Bear)
Entity(Bruno)
InstanceOf(Bruno, Bear)
```

Expect Bear in `concepts_of(Bruno)`.

## S103 — Instance Inheritance

```text
SubtypeOf(Bear, Animal)
InstanceOf(Bruno, Bear)
```

Expect derived `InstanceOf(Bruno, Animal)` and both concepts in query results.

## S104 — Transitive Subtype

```text
Penguin <: Bird
Bird <: Animal
```

Expect `Penguin <: Animal` with provenance through both premises.

## S105 — Multiple Inheritance

```text
Bat <: Mammal
Bat <: FlyingCreature
Bruce : Bat
```

Expect Bruce to inherit both concepts.

## S106 — Unknown Membership

```text
Entity(Kiki)
Concept(Bird)
```

with no membership support.

Expect `InstanceOf(Kiki, Bird) == UNKNOWN`, not false.

## S107 — Concept Also Entity

```text
Concept(Fire)
Entity(Fire)
```

Expect both to coexist.

## S108 — Dynamic Number Attribute

```text
AttributeDef(Health)
AttributeNumber(Bruno, Health, 80)
```

Expect attribute query value `80`.

## S109 — Multi-Valued Attribute

```text
AttributeDef(FavoriteColor)
AttributeString(Alice, FavoriteColor, "red")
AttributeString(Alice, FavoriteColor, "blue")
```

Expect both values and no automatic contradiction.

## S110 — Dynamic Binary Relation

```text
RelationDef(ParentOf)
Related(ParentOf, Alice, Bob)
```

Expect Bob from ParentOf(Alice, ?).

## S111 — Label Is Not Identity

```text
Label(A, "Dragon")
Label(B, "Dragon")
```

Expect distinct IDs.

## S112 — Subtype Cycle

```text
SubtypeOf(A, B)
SubtypeOf(B, A)
```

Expect deterministic termination plus subtype-cycle diagnostic.

## S113 — Query Uses Derived View

Only direct:

```text
InstanceOf(Bruno, Bear)
SubtypeOf(Bear, Animal)
```

Expect `concepts_of(snapshot, Bruno)` to include derived Animal.

## S114 — Inheritance Provenance

Why-query for:

```text
InstanceOf(Bruno, Animal)
```

must include:

```text
InstanceOf(Bruno, Bear)
SubtypeOf(Bear, Animal)
swm.rule.instance_inheritance
```

## S115 — Atomic Builder

Cause one operation in a multi-operation builder patch to be invalid.

Expect no partial Standard World Model edit to be committed.


## 27. Additional Unit Tests

Cover at least:

```text
vocabulary schemas have expected argument kinds
schema names are stable

builders create expected propositions
builders preserve source
builders never mutate World directly
builder operation ordering is deterministic

queries consume SemanticSnapshot
query ordering is deterministic

typed attribute queries do not cross-read other value kinds

world-defined relation IDs are independent of labels

subtype diagnostics are deterministic

all P0 tests remain green
```


## 28. Recommended Milestone Sequence

```text
P1.0
worldmodel package skeleton + vocabulary

P1.1
Concept / Entity / Label builders and queries

P1.2
InstanceOf / SubtypeOf
+ transitivity and instance inheritance DERIVE rules

P1.3
Typed attributes
+ attribute builders/queries

P1.4
RelationDef / Related
+ relation builders/queries

P1.5
Standard runtime composition helpers

P1.6
Diagnostics
+ subtype cycle

P1.7
S101–S115 conformance suite

P1.8
Documentation / ADR / hardening
```

Use small reviewable commits.


## 29. Suggested Public API

Tentative exports:

```text
vocabulary constants

standard_world_rules()
standard_world_runtime()

define_concept()
create_entity()

define_attribute()
add_number_attribute()
add_string_attribute()
add_boolean_attribute()
add_reference_attribute()

define_relation()
add_related()

labels_of()
concepts_of()
instances_of()
subtypes_of()
supertypes_of()

number_attribute_values()
string_attribute_values()
boolean_attribute_values()
reference_attribute_values()

related_objects()
relations_between()

diagnose_world_model()
```

Do not export incidental internal helpers without need.


## 30. Determinism

Equivalent semantic inputs must not change P1 output based on incidental container order.

Use stable ordering for:

```text
builder operations
query results
rule collections
diagnostics
generated occurrence IDs
```

Do not rely on unordered set/dict iteration as semantic behavior.


## 31. Provenance

P1 reuses P0 provenance.

Do not invent a second explanation system.

Standard inference rules need stable IDs.

Builder direct supports need meaningful source metadata.

The future natural-language explanation layer will consume P0 why-graphs plus P1 vocabulary.


## 32. Hard Non-Goals

Do NOT implement in P1:

- State / Event / Transition;
- Time / ordering;
- Space / position;
- movement or collision;
- physics;
- continuous/rate rules;
- probability/RNG;
- aggregates;
- n-ary world-defined relations;
- class-level inherited attribute defaults;
- subtype-specific DEFAULT priority;
- closed-world semantics;
- NOT_KNOWN;
- existential entity creation in DERIVE;
- LLM parser/compiler;
- natural-language query;
- database persistence;
- UI;
- Godot/Unity/Unreal;
- generated assets;
- multiplayer.

Do not solve future milestones opportunistically.


## 33. Kernel Protection Rules

P1 MUST NOT:

```text
add Entity as a worldkernel primitive
add Concept as a worldkernel primitive
add inheritance semantics inside worldkernel
teach worldkernel about labels
teach worldkernel about attributes
teach worldkernel about world-defined relation semantics
```

If a Kernel modification is genuinely unavoidable, create an ADR explaining the limitation, proposed change, and alternatives before proceeding.


## 34. Documentation Requirements

Add/update:

```text
README.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/P1_STANDARD_WORLD_MODEL.md
```

Recommended new docs:

```text
docs/worldmodel/VOCABULARY.md
docs/worldmodel/ONTOLOGY.md
docs/worldmodel/ATTRIBUTES.md
docs/worldmodel/RELATIONS.md
docs/worldmodel/QUERIES.md
docs/worldmodel/DIAGNOSTICS.md
```

Add an ADR documenting:

> Player-defined concepts, attributes, and relations are world data expressed through fixed Standard World Model vocabulary, not new Meta-Kernel primitives.

Suggested name:

```text
ADR 0010 — Standard World Model as Library Vocabulary
```


## 35. README Status

During implementation:

```text
P0 — Semantic Kernel Reference Implementation: COMPLETE
P1 — Standard World Model v0: IN PROGRESS
```

After completion criteria pass:

```text
P1 — Standard World Model v0: COMPLETE
```

Do not claim simulation support.


## 36. CI

Existing GitHub Actions remains authoritative:

```text
python -m pip install -e ".[test]"
python -m pytest -q
```

All P0 tests remain mandatory.


## 37. P1 Completion Criteria

P1 is complete only when:

- [ ] `worldmodel` exists separately from `worldkernel`;
- [ ] dependency direction is only `worldmodel -> worldkernel`;
- [ ] fixed P1 vocabulary is implemented;
- [ ] Concept and Entity roles work;
- [ ] labels are separate from IDs;
- [ ] one ID may be both Concept and Entity;
- [ ] InstanceOf works;
- [ ] SubtypeOf works;
- [ ] subtype transitivity works through DERIVE;
- [ ] instance inheritance works through DERIVE;
- [ ] multiple inheritance works;
- [ ] subtype cycles terminate and emit diagnostics;
- [ ] typed attributes work;
- [ ] attributes are multi-valued by default;
- [ ] world-defined binary relations work;
- [ ] dynamic world definitions do not create Kernel primitives;
- [ ] builders return atomic WorldPatch objects;
- [ ] builders never mutate World directly;
- [ ] builder occurrence IDs obey P0 history semantics;
- [ ] semantic queries consume evaluated SemanticSnapshot;
- [ ] inherited membership appears in queries;
- [ ] inheritance provenance is correct;
- [ ] S101–S115 all pass;
- [ ] all existing P0 tests still pass;
- [ ] GitHub Actions full suite passes;
- [ ] no State/Event/Time/Space/Physics primitive is introduced;
- [ ] docs accurately describe P1.


## 38. Required Final Report From Codex

At completion report:

1. commits created;
2. packages/files added;
3. any `worldkernel` files modified and why;
4. exact Standard World Model vocabulary;
5. standard DERIVE rules;
6. builder APIs;
7. query APIs;
8. diagnostics;
9. builder support-occurrence ID policy;
10. conformance tests added;
11. exact full-suite pytest result;
12. GitHub Actions result;
13. ADR/documentation updates;
14. any deferred requirement;
15. confirmation that no P1 concept became a Meta-Kernel primitive;
16. confirmation that P0 behavior/tests remain intact.


## 39. P1 Exit / Next Milestone

Do not begin simulation/change semantics in this task.

After P1 completion, the next design milestone should separately examine:

```text
State
Change
Action
Event
Transition
Ordering
Simulation phases
```

without assuming that `Time`, `State`, or `Event` must become Kernel primitives.

P1 should end with a useful static/deductive world ontology layer, not a moving game world.
