"""P0.8 snapshot-evaluated triggers producing atomic patch commits."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from .model import OpaqueId
from .pattern import PropositionPattern, SupportPattern, Variable, match_support
from .support import DirectSupport, SupportPolarity
from .world import AddDirectSupport, World, WorldPatch

@dataclass(frozen=True, slots=True)
class TriggerAdd:
    proposition: PropositionPattern
    polarity: SupportPolarity
@dataclass(frozen=True, slots=True)
class TriggerRule:
    rule_id: OpaqueId
    premises: tuple[SupportPattern, ...]
    outputs: tuple[TriggerAdd, ...]

def run_trigger_phase(world: World, rules: tuple[TriggerRule, ...]) -> World:
    """Evaluate every trigger against one frozen revision, then commit once."""
    snapshot = tuple(world.current.supports)
    operations = []
    for rule in sorted(rules, key=lambda item: item.rule_id.value):
        for bindings in _matches(rule.premises, snapshot):
            for output in rule.outputs:
                proposition = output.proposition.relation.apply(*(bindings[item] if isinstance(item, Variable) else item for item in output.proposition.arguments))
                payload = repr((rule.rule_id.value, proposition, output.polarity.name))
                support_id = OpaqueId(f"trigger-{hashlib.sha256(payload.encode()).hexdigest()}")
                operations.append(AddDirectSupport(support_id, proposition, output.polarity, f"trigger:{rule.rule_id.value}"))
    if not operations:
        return world
    patch_id = OpaqueId(f"trigger-phase-{hashlib.sha256(repr(tuple(operations)).encode()).hexdigest()}")
    return world.commit(WorldPatch(patch_id, tuple(operations), "trigger"))

def _matches(premises: tuple[SupportPattern, ...], supports: tuple[DirectSupport, ...]):
    matches = [dict()]
    for premise in premises:
        next_matches = []
        for bindings in matches:
            for support in supports:
                resolved = match_support(premise, support, bindings)
                if resolved is not None:
                    next_matches.append(resolved)
        matches = next_matches
    return tuple(matches)
