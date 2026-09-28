# World Definition Game — Semantic Kernel Starter

This repository is the starting specification for a simulation game in which players define the concepts, relations, laws, and objects of a world rather than merely arranging pre-authored content.

The long-term experience is:

> imagine → define in natural language → formalize → validate → apply → simulate → observe → ask why → revise

The LLM is intended to act as a compiler/front-end from player intent to structured world changes. The authoritative world is a deterministic semantic runtime with provenance, not an LLM conversation state.

## Repository status
The **P0: Semantic Kernel Reference Implementation** is in progress. P0.9
adds machine-readable justification graphs that retain support paths, rule
IDs, premise edges, and revision context.

## Development
```text
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[test]"
.venv/Scripts/python -m pytest
```

## Read first
1. `docs/VISION.md`
2. `docs/ARCHITECTURE.md`
3. `docs/P0_SCOPE.md`
4. `docs/semantics/META_KERNEL.md`
5. `docs/semantics/PROPOSITION_SUPPORT.md`
6. `docs/semantics/RULE_SEMANTICS.md`
7. `docs/scenarios/README.md`
8. `AGENTS.md`

## Core idea
The engine should distinguish four layers:

1. **Meta-Kernel** — minimal language for describing and changing worlds.
2. **Standard World Model** — optional libraries such as Entity, State, Time, Space, Event, Cause.
3. **Domain Modules / Presets** — physics, biology, society, Modern Earth, fantasy, etc.
4. **Player World** — additions, deletions, overrides, and new definitions.

A player may begin from a rich preset ("Modern Earth, but gravity ×10"), a general world model, or eventually a near-blank world built almost from the Meta-Kernel upward.

## Guiding principle
If two worlds produce the same observable trajectory but describe it differently, the semantic engine should care about the operational model that produces the trajectory, not force a philosophical label. Terms such as Time, Cause, Life, and Identity belong above the Meta-Kernel unless proven otherwise.
