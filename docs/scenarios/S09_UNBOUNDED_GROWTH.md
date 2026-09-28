# S09 — Unbounded Growth

**Milestone:** Deferred (P2)

## Intent
A rule causes every rabbit to create another rabbit, whose existence would recursively trigger the same behavior.

## Required future behavior
- The world definition may be semantically allowed.
- Runtime resource budgets prevent host failure.
- Budget exhaustion produces a diagnostic/suspension, not a philosophical assertion that the world is invalid.
