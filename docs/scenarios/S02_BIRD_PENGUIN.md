# S02 — Bird / Penguin

**Milestone:** P0

## Rules
```text
DERIVE Penguin(?x) -> +Bird(?x)
DEFAULT Bird(?x) -> +CanFly(?x)
DERIVE Penguin(?x) -> -CanFly(?x)
```

## Given
```text
+Penguin(Pingu)
```

## Expect
- `Bird(Pingu)` receives positive derived support.
- `CanFly(Pingu)` receives a positive default support.
- `CanFly(Pingu)` receives a negative non-default derived support.
- The default positive support is defeated but retained in provenance.
- Effective status of `CanFly(Pingu)` is `FALSE_ONLY`.

## Purpose
Validates defeasible defaults without erasing explanation history.
