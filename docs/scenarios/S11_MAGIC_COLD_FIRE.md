# S11 — Magic Cold Fire

**Milestone:** Partly P0, full package behavior deferred

## Rules
```text
DEFAULT Fire(?x) -> +Hot(?x)
DERIVE MagicColdFire(?x) -> +Fire(?x)
DERIVE MagicColdFire(?x) -> -Hot(?x)
```

## Given
`MagicColdFire(BlueFlame)`.

## Expect
The positive default for Hot is defeated by explicit/non-default negative support, producing effective FALSE_ONLY.

## Extension
If a non-default positive support for Hot is added, status becomes CONFLICT rather than being silently resolved by specificity.
