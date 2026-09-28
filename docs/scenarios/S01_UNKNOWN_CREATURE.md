# S01 — Unknown Creature

**Milestone:** P0

## Given
```text
Creature(Kiki)
HasWing(Kiki)
```
No support exists for `CanFly(Kiki)` in either polarity.

## Expect
```text
status(CanFly(Kiki)) == UNKNOWN
```

## Must not
Infer negative support merely because positive support is absent.

## Purpose
Validates open-world semantics and Unknown ≠ False.
