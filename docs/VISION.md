# Vision

## Product thesis
Create a simulation game where the player defines what kinds of things exist, what relations and laws connect them, and how those definitions produce consequences over time.

The game's primary creative act is not object placement. It is **world definition**.

Examples of intended player requests:
- "Create a bear with four wings. The upper pair is for flight; the lower pair regulates temperature."
- "Birds normally fly, but penguins do not."
- "In this world, blue objects are pulled upward instead of downward."
- "Start from modern Earth, but make surface gravity ten times stronger."
- "Death should no longer end consciousness, although metabolism and bodily decay continue."
- "Build a world from scratch where locations are graph nodes rather than Euclidean coordinates."

## Player fantasy
The player is closer to a creator, modeler, and investigator than to a conventional avatar. The player can:
- define concepts and objects;
- define relations and laws;
- alter existing presets;
- observe emergent consequences;
- ask why something happened;
- revise definitions;
- fork worlds and compare counterfactuals.

## Core gameplay loop
1. Imagine a change or concept.
2. Express it in natural language or structured UI.
3. Review the formalized interpretation when necessary.
4. Apply an atomic world change.
5. Let the simulation run.
6. Observe expected and unexpected consequences.
7. Ask "why?" and inspect causal/provenance traces.
8. Modify definitions and repeat.

## Design goals
### Freedom without requiring programming knowledge
Natural language should be the primary high-level interface. The player should not need to write code, though advanced users may inspect or edit formal definitions.

### Semantic authority outside the LLM
The LLM interprets player intent. It does not decide runtime truth frame-by-frame. Once compiled, world semantics are executed by deterministic systems.

### Observable consequences over labels
"Reverse time" is not meaningful unless it is operationalized. The game should translate high-level phrases into explicit semantics and expose what they mean.

### Explainability as gameplay
Every important derived state or mutation should be traceable. "Why did this rabbit die?" should have an answer based on recorded supports, rules, and events, not generated guesswork.

### Layered starting points
Players should be able to begin at different depths:
- **Blank / Genesis**: near-Meta-Kernel start.
- **Basic World**: general space/time/object/life libraries.
- **Modern Earth**: a practical counterfactual sandbox.
- **Community Presets**: reusable world-definition packages.

## Non-goals of the initial project
The first implementation is not attempting:
- a perfect simulation of reality;
- universal philosophical formalization;
- a theorem prover for arbitrary logics;
- photorealistic generative 3D;
- autonomous LLM agents for every NPC;
- a complete social/economic/biological model.

The first goal is to prove that defining and debugging a world is itself enjoyable and technically coherent.
