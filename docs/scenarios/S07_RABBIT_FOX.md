# S07 — Rabbit / Fox Ecology

**Milestone:** Deferred (P2+)

## Intent
Plants regrow, rabbits eat plants and reproduce, foxes eat rabbits and reproduction depends on food availability.

## Purpose
Validates the later loop:
```text
semantic closure -> simulation step -> patch -> next revision
```
The world need not reach a global fixed point; only each logical inference phase must settle.
