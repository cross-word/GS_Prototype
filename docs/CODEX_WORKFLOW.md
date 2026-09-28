# Codex Workflow

## Working model
Codex should implement narrowly scoped milestones against stable specifications and tests. Architectural decisions belong in specs/ADRs before implementation.

## Recommended task shape
Bad:
> Build the semantic engine.

Good:
> Implement P0.2 positive/negative support storage and effective four-state status. Do not implement rule evaluation. Add unit tests and S01 conformance behavior. Preserve all invariants in AGENTS.md.

## Per-task checklist
1. Read `AGENTS.md`.
2. Read the relevant semantic spec and ADR.
3. Identify the exact milestone and non-goals.
4. Add/confirm failing tests.
5. Implement minimal behavior.
6. Run focused tests.
7. Run all P0 tests.
8. Summarize changed semantics and files.
9. Do not broaden scope without an explicit follow-up task.

## Escalation rule
If a task requires choosing among materially different semantics not already specified, do not pick silently. Create a short design note describing the ambiguity and the implementation consequences.

## Suggested first implementation sequence
- P0.1 IDs / Values / Relations / Propositions
- P0.2 Supports / status
- P0.3 Pattern matching
- P0.4 DERIVE
- P0.5 Truth maintenance
- P0.6 DEFAULT
- P0.7 WorldPatch
- P0.8 TRIGGER
- P0.9 Provenance query API
- P0.10 Conformance suite
