"""P0.8 snapshot-evaluated triggers producing atomic patch commits."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from .model import OpaqueId
from .expressions import Expression, evaluate_guard, expression_variables
from .errors import InvalidRuleError
from .canonical import canonical_proposition
from .pattern import PropositionPattern, SupportPattern, Variable, match_support
from .support import Support, SupportPolarity
from .world import AddDirectSupport, World, WorldPatch

@dataclass(frozen=True, slots=True)
class TriggerAdd:
    proposition: PropositionPattern
    polarity: SupportPolarity

    def __post_init__(self) -> None:
        if not isinstance(self.proposition, PropositionPattern):
            raise InvalidRuleError("trigger.invalid_output_proposition", "A TRIGGER output requires a proposition pattern.")
        if not isinstance(self.polarity, SupportPolarity):
            raise InvalidRuleError("trigger.invalid_output_polarity", "A TRIGGER output requires a recognized polarity.")
@dataclass(frozen=True, slots=True)
class TriggerRule:
    rule_id: OpaqueId
    premises: tuple[SupportPattern, ...]
    outputs: tuple[TriggerAdd, ...]
    guard: Expression | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, OpaqueId):
            raise InvalidRuleError("trigger.invalid_rule_id", "A TRIGGER rule must have an opaque rule ID.")
        try:
            premises = tuple(self.premises)
        except TypeError as error:
            raise InvalidRuleError("trigger.invalid_premises", "TRIGGER premises must be iterable support patterns.") from error
        if not premises or not all(isinstance(premise, SupportPattern) for premise in premises):
            raise InvalidRuleError("trigger.invalid_premises", "A TRIGGER rule requires one or more support-pattern premises.")
        try:
            outputs = tuple(self.outputs)
        except TypeError as error:
            raise InvalidRuleError("trigger.invalid_outputs", "TRIGGER outputs must be iterable trigger additions.") from error
        if not outputs or not all(isinstance(output, TriggerAdd) for output in outputs):
            raise InvalidRuleError("trigger.invalid_outputs", "A TRIGGER rule requires one or more trigger additions.")
        premise_variables = {argument for premise in premises for argument in premise.proposition.arguments if isinstance(argument, Variable)}
        output_variables = {argument for output in outputs for argument in output.proposition.arguments if isinstance(argument, Variable)}
        unbound_outputs = sorted(variable.name for variable in output_variables - premise_variables)
        if unbound_outputs:
            raise InvalidRuleError("trigger.unbound_output_variable", "Every TRIGGER output variable must be bound by a premise.", {"variables": unbound_outputs})
        if self.guard is not None:
            try:
                unbound_guard = expression_variables(self.guard) - premise_variables
            except Exception as error:
                raise InvalidRuleError("trigger.invalid_guard", "A TRIGGER guard must be a recognized expression.") from error
            if unbound_guard:
                raise InvalidRuleError("trigger.unbound_guard_variable", "Every TRIGGER guard variable must be bound by a premise.", {"variables": sorted(variable.name for variable in unbound_guard)})
        object.__setattr__(self, "premises", premises)
        object.__setattr__(self, "outputs", outputs)

def run_trigger_phase(world: World, rules: tuple[TriggerRule, ...], snapshot_supports: tuple[Support, ...] | None = None) -> World:
    """Evaluate every trigger against one frozen revision, then commit once."""
    snapshot = tuple(world.current.supports) if snapshot_supports is None else tuple(snapshot_supports)
    operations = []
    for rule in sorted(rules, key=lambda item: item.rule_id.value):
        for bindings in _matches(rule.premises, snapshot):
            if not evaluate_guard(rule.guard, bindings):
                continue
            for output in rule.outputs:
                proposition = output.proposition.relation.apply(*(bindings[item] if isinstance(item, Variable) else item for item in output.proposition.arguments))
                payload = repr((rule.rule_id.value, canonical_proposition(proposition), output.polarity.name))
                support_id = OpaqueId(f"trigger-{hashlib.sha256(payload.encode()).hexdigest()}")
                operations.append(AddDirectSupport(support_id, proposition, output.polarity, f"trigger:{rule.rule_id.value}"))
    existing = {item.support_id for item in world.current.supports}
    unique = {item.support_id: item for item in operations if item.support_id not in existing}
    operations = [unique[key] for key in sorted(unique, key=lambda item: item.value)]
    if not operations:
        return world
    patch_payload = tuple((operation.support_id.value, canonical_proposition(operation.proposition), operation.polarity.name, operation.origin) for operation in operations)
    patch_id = OpaqueId(f"trigger-phase-{hashlib.sha256(repr(patch_payload).encode()).hexdigest()}")
    return world.commit(WorldPatch(patch_id, tuple(operations), "trigger"))

def _matches(premises: tuple[SupportPattern, ...], supports: tuple[Support, ...]):
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
