# S03 — Contradictory Dragon

**Milestone:** P0

## Rules
```text
DERIVE Dragon(?x) -> +Mortal(?x)
DERIVE Dragon(?x) -> -Mortal(?x)
DERIVE +Mortal(?x) -> +HasFiniteLife(?x)
DERIVE -Mortal(?x) -> +Eternal(?x)
```

## Given
```text
+Dragon(Smaug)
```

## Expect
- `Mortal(Smaug)` is `CONFLICT`.
- `HasFiniteLife(Smaug)` is positively supported.
- `Eternal(Smaug)` is positively supported.
- No unrelated proposition is derived merely from the contradiction.

## Purpose
Validates limited paraconsistent behavior and contradiction propagation without explosion.
