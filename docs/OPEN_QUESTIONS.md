# Open Questions

These questions are deliberately **not blockers for starting P0** unless an implementation task reaches them directly.

## Near-term semantic questions
### Default-vs-default conflict
If opposite DEFAULT rules both apply, P0 currently preserves both candidates rather than inventing specificity. Later we may add explicit priority or structured specificity.

### Relation schema richness
P0 requires arity and basic argument well-formedness. Later choices include relation-level cardinality, functional constraints, symmetry/transitivity metadata, and open/closed-world policy.

### Exact patch merge semantics for simultaneous writes
Snapshot evaluation is frozen, but richer property-update conflicts are deferred until property conventions exist in the Standard World Model.

### Expression type system
P0 needs deterministic scalar expressions. Numeric subtypes, vectors, sets, units, approximate equality, and user-defined functions remain open.

## Later simulation questions
- representation of world-level time;
- continuous/rate dynamics;
- deterministic RNG API;
- event queue semantics;
- resource-budget behavior for intentionally explosive worlds;
- aggregates such as COUNT/SUM/AVG;
- causal explanation vs provenance explanation.

## Later world-model questions
- how Standard World Model defines Entity and Concept;
- subtype/default specificity;
- identity as a world-level concept;
- space packages (Euclidean, graph-based, other);
- preset/module override layering;
- approximation metadata for "Modern Earth" modules.

## Later product questions
- when natural-language interpretation requires confirmation vs auto-commit;
- advanced structured editor design;
- world fork/comparison UX;
- community preset/package distribution;
- generative 3D and semantic-part representation.

## Rule for handling an open question
If implementation encounters one of these questions and different choices would change externally observable semantics, write an ADR before coding the choice.
