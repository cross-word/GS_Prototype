# S14 — Probabilistic Reproduction

**Milestone:** Deferred (P2)

## Intent
"Each spring this creature reproduces with 30% probability."

## Required future behavior
Same initial revision + same deterministic seed/event identity should reproduce the same result and replay history.

Randomness must be explicit and replayable rather than hidden inside arbitrary runtime calls.
