# ADR 0010 — Standard World Model as Library Vocabulary

**Status:** Accepted for P1

## Decision

P1 implements concepts, entities, attributes, and player-defined binary
relations as world data expressed through a fixed `worldmodel` vocabulary. They
are not Meta-Kernel primitives and `worldkernel` does not depend on P1.

## Consequence

For example, a player-defined relation is represented by `swm.RelationDef` and
`swm.Related`, rather than dynamically creating a new Kernel primitive.
