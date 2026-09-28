# First Codex Task — P0.1

Use this after creating the repository and placing these specification files in it.

## Task
Implement **P0.1: IDs, scalar values, relation schemas, and propositions** only.

Read `AGENTS.md`, `docs/DESIGN_FREEZE.md`, `docs/P0_SCOPE.md`, `docs/semantics/META_KERNEL.md`, and relevant ADRs before editing.

### Requirements
1. Set up a minimal Python package for `worldkernel` and pytest-based tests.
2. Implement an opaque ID type or representation with deterministic equality and a safe string representation.
3. Implement P0 scalar values sufficient for Number, Boolean, and String without introducing world-level Quantity/units.
4. Implement relation schemas with:
   - stable relation identity/name;
   - arity;
   - minimal argument-kind/type validation.
5. Implement propositions as immutable, hashable relation applications.
6. Reject malformed propositions with structured exceptions/errors.
7. Do **not** implement Support, rules, patches, provenance graphs, Entity/Concept/State/Time, persistence, or LLM code yet.
8. Add focused unit tests.
9. Add the minimum fixture needed for S01 later, but do not prematurely implement S01 truth status because Support belongs to P0.2.
10. Run the full test suite and report results.

### Design constraints
- Do not make Relation a subclass of an Entity concept.
- Do not add `is_true` or any truth field to Proposition.
- Do not make absent propositions implicitly false.
- Keep the semantic package independent of game engines and external AI libraries.
- Prefer straightforward data classes/value objects over frameworks.

### Deliverable
A small, tested P0.1 implementation that provides the structural vocabulary required for P0.2 and does not implement later semantics early.
