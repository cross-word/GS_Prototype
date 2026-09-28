# Evaluation Model v0

## Determinism
Given the same initial revision, same committed patch sequence, and same explicit seed inputs once randomness exists, the semantic runtime should produce the same history.

P0 contains no randomness.

## Fixed point
DERIVE evaluation stops when no new active derived support or justification state changes occur.

Resource safeguards should exist to detect implementation bugs or unexpectedly unbounded rule graphs, but a normal finite derivation graph should settle by duplicate detection and truth maintenance.

## Default phase
DEFAULT rules are evaluated after ordinary derivation closure for the current revision. Their candidate supports are then filtered by the v0 defeat policy.

## Trigger phase
TRIGGER evaluation occurs only after the effective semantic view for the snapshot is stable.

## Resource policy
P0 should expose bounded safety controls for testing, such as:
- maximum derivation iterations;
- maximum generated support records per evaluation;
- maximum trigger firings per phase.

Hitting a limit is a runtime diagnostic, not a semantic conclusion about the world.

## Future simulation relationship
Later simulation milestones may repeatedly execute:
```text
semantic closure
→ simulation/event step
→ patch
→ next revision
```
World-level Time remains a library concept and must not be equated with this host execution loop.
