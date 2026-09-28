# Architecture

## Layer model

```text
Player / UI
    │
    ▼
Intent compiler (future LLM front-end)
    │
    ▼
WorldPatch proposal
    │
    ▼
Validation / dry-run
    │
    ▼
┌──────────────────────────────┐
│        Semantic Runtime      │
│                              │
│  Meta-Kernel                 │
│  Standard World Libraries   │
│  Domain Modules / Presets   │
│  Player Overrides           │
└──────────────┬───────────────┘
               │
      ┌────────┼─────────┐
      ▼        ▼         ▼
 Simulation  Physics   Asset system
               │
               ▼
           Game client
```

## Semantic layering

```text
PLAYER WORLD
- player additions
- deletions
- overrides
- custom definitions

DOMAIN MODULES / PRESETS
- physics
- biology
- ecology
- society
- economy
- Modern Earth
- fantasy packages

STANDARD WORLD MODEL
- Entity
- Concept
- Property
- State
- Event
- Transition
- Time
- Space / Position
- Cause
- Action
- Quantity

META-KERNEL
- ID
- Value
- Relation
- Proposition
- Support
- Variable / Pattern
- Expression
- Rule
- WorldPatch

ENGINE RUNTIME
- memory / persistence
- transaction engine
- indexes
- scheduler
- provenance store
- revision history
```

## Dependency direction
Dependencies point downward only.

- Player/domain libraries may depend on Standard World Model and Meta-Kernel.
- Standard World Model may depend on Meta-Kernel.
- Meta-Kernel must not depend on any higher layer.
- Rendering and asset systems may read semantic state but must not define semantic truth implicitly.

## Semantic vs visual representation
A semantic object is not its mesh.

Example:
```text
Semantic definition:
  Bear
  Wing ×4
  Flight via upper wings
  Thermoregulation via lower wings

Visual representation:
  mesh / material / rig / animation
```

Changing visual appearance must not silently change semantics. Changing semantics must not require regenerating visuals unless representation becomes incompatible.

## LLM role
The LLM is a compiler/front-end and explainer.

Allowed roles:
- interpret natural-language intent;
- retrieve relevant world definitions;
- propose structured WorldPatch objects;
- explain provenance traces;
- propose clarifications for ambiguous high-level concepts.

Disallowed authority:
- direct mutation outside WorldPatch;
- frame-by-frame truth decisions;
- silently inventing world laws not represented in the semantic runtime.

## Simulation phases
Target conceptual phase model:

```text
Committed revision
    ↓
DERIVE closure
    ↓
DEFAULT resolution
    ↓
Effective semantic view
    ↓
Simulation snapshot
    ↓
TRIGGER / later continuous systems
    ↓
WorldPatch
    ↓
Validate
    ↓
Atomic commit
    ↓
Next revision
```

P0 implements only enough of this to validate the semantic model. Continuous dynamics, physics, and advanced scheduling are later milestones.

## Presets as composition, not separate engines
Presets should be reusable packages and overrides.

Example:
```text
ModernEarth@1.0
  imports StandardWorld
  imports RealisticPhysics
  imports EarthBiology
  imports HumanSociety

PlayerWorld
  base = ModernEarth@1.0
  override GravityAcceleration(EarthSurface) = 98.1
```

Worlds should be forkable and comparable without cloning unrelated implementation logic.
