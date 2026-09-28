# S05 — Glass Break

**Milestone:** P0

## Given
```text
+Glass(Cup)
+Collision(Cup, Ground)
```

## Trigger
```text
TRIGGER
  Collision(?x, Ground) AND Glass(?x)
THEN PATCH
  ADD +Broken(?x)
```

## Expect after trigger commit
```text
Broken(Cup) == TRUE_ONLY
```

## When
The direct support for `Collision(Cup, Ground)` is later removed.

## Expect
`Broken(Cup)` remains supported because it was persistently added by a committed trigger patch rather than maintained as a logical derivation.

## Purpose
Separates state mutation from logical implication.
