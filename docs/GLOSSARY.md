# Glossary

## ID
Opaque runtime identifier used to refer to a record or symbol. An ID is not a philosophical claim of identity.

## Value
Literal runtime data such as number, boolean, or string. Additional structured value types may be introduced later.

## Relation
A named schema for an n-ary relationship, including at minimum arity and argument well-formedness constraints.

## Proposition
A well-formed relation applied to arguments, e.g. `CanFly(Pingu)` or `ParentOf(Alice, Bob)`. A proposition does not itself encode whether it is supported positively or negatively.

## Support
A positive or negative reason for a proposition. Supports carry origin and justification information.

## Effective status
The status computed from active positive and negative supports:
- `UNKNOWN`: neither polarity supported.
- `TRUE_ONLY`: positive support only.
- `FALSE_ONLY`: negative support only.
- `CONFLICT`: both positive and negative support.

## Explicit support
Support introduced directly by a committed patch or by a non-default rule whose premises are supported.

## Default support
Defeasible support introduced by a DEFAULT rule and suppressible by stronger contrary support according to the default-resolution policy.

## Pattern
A proposition-like structure containing variables and used to match current semantic state.

## DERIVE rule
A logical rule whose conclusion is supported while its premises are supported. Derived support is truth-maintained.

## DEFAULT rule
A defeasible derivation used when no defeating contrary support applies.

## TRIGGER rule
A state-changing rule evaluated against a committed snapshot that proposes a WorldPatch. Its result persists as a world mutation rather than merely as a logical consequence.

## WorldPatch
An atomic proposed change to persistent semantic state. It must validate as a whole before commit.

## Revision
An immutable identifier for a committed world state transition.

## Provenance
The recorded explanation of where support or mutation came from and what prior data justified it.

## Standard World Model
Optional libraries that define common world concepts such as Entity, Concept, State, Event, Time, Space, Cause, and Quantity using Meta-Kernel machinery.

## Meta-Kernel
The minimal, domain-neutral semantic language/runtime that higher-level world models are built upon.
