# ADR 0001 — Meta-Kernel Boundary

**Status:** Accepted for P0

## Decision
The Meta-Kernel contains only domain-neutral machinery: ID, Value, Relation, Proposition, Support, Variable/Pattern, Expression, Rule, and WorldPatch.

Entity, Concept, Property, State, Event, Transition, Time, Space, Position, Cause, Action, and Quantity are not Meta-Kernel primitives.

## Rationale
Hard-coding these concepts would force a particular ontology of worlds and undermine the long-term goal of allowing radically different world models.

## Consequence
Common concepts require a Standard World Model library later. P0 may therefore feel more abstract than a conventional game engine.
