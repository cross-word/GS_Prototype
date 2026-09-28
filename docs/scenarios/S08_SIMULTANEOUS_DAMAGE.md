# S08 — Simultaneous Damage

**Milestone:** P0

## Snapshot
```text
Health(Bob, 100)
Attack(Alice, Bob, 30)
Attack(Carol, Bob, 40)
```

## Intent
Both attacks occur in the same trigger phase.

## Expect
- Both trigger conditions observe `Health(Bob, 100)` / the same committed snapshot.
- No trigger sees another trigger's intermediate mutation.
- Patch resolution is deterministic.

## Note
P0 need not implement a full numeric property merge language. The test may use two non-conflicting persistent outputs or an explicit deterministic merge fixture. The semantic requirement is snapshot isolation, not a specific health arithmetic API.
