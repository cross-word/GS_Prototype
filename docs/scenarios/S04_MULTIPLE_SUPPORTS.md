# S04 — Multiple Supports

**Milestone:** P0

## Rules
```text
DERIVE Bird(?x) -> +Animal(?x)
DERIVE Penguin(?x) -> +Animal(?x)
```

## Given
```text
+Bird(Toto)
+Penguin(Toto)
```

## Then
`Animal(Toto)` has at least two independent positive justification paths.

## When
The direct support for `Bird(Toto)` is retracted.

## Expect
`Animal(Toto)` remains `TRUE_ONLY` through the Penguin derivation.

## Purpose
Validates truth maintenance and justification-path independence.
