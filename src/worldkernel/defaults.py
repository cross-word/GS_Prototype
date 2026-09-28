"""P0.6 defeasible DEFAULT rule evaluation."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .errors import InvalidRuleError
from .expressions import Expression, evaluate_guard, expression_variables
from .model import KernelArgument, OpaqueId, Proposition
from .pattern import Bindings, PropositionPattern, SupportPattern, Variable, match_support
from .support import DefaultSupport, DerivedSupport, DirectSupport, Support, SupportPolarity


@dataclass(frozen=True, slots=True)
class DefaultRule:
    """A defeasible rule evaluated after ordinary DERIVE closure."""

    rule_id: OpaqueId
    premises: tuple[SupportPattern, ...]
    conclusion: PropositionPattern
    conclusion_polarity: SupportPolarity
    guard: Expression | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, OpaqueId):
            raise InvalidRuleError("default.invalid_rule_id", "A DEFAULT rule must have an opaque rule ID.")
        try:
            premises = tuple(self.premises)
        except TypeError as error:
            raise InvalidRuleError("default.invalid_premises", "DEFAULT premises must be iterable.") from error
        if not premises or not all(isinstance(item, SupportPattern) for item in premises):
            raise InvalidRuleError("default.invalid_premises", "A DEFAULT rule requires support-pattern premises.")
        if not isinstance(self.conclusion, PropositionPattern):
            raise InvalidRuleError("default.invalid_conclusion", "A DEFAULT conclusion must be a proposition pattern.")
        if not isinstance(self.conclusion_polarity, SupportPolarity):
            raise InvalidRuleError("default.invalid_conclusion_polarity", "A DEFAULT rule requires a recognized polarity.")
        premise_variables = {
            argument for premise in premises for argument in premise.proposition.arguments if isinstance(argument, Variable)
        }
        unbound = sorted({argument.name for argument in self.conclusion.arguments if isinstance(argument, Variable) and argument not in premise_variables})
        if unbound:
            raise InvalidRuleError("default.unbound_conclusion_variable", "Every DEFAULT conclusion variable must be bound by a premise.", {"variables": unbound})
        if self.guard is not None and not expression_variables(self.guard) <= premise_variables:
            raise InvalidRuleError("default.unbound_guard_variable", "Every DEFAULT guard variable must be bound by a premise.")
        object.__setattr__(self, "premises", premises)


def evaluate_defaults(rules: Iterable[DefaultRule], supports: Iterable[Support]) -> tuple[Support, ...]:
    """Generate default candidates from ordinary support without erasing defeats."""

    rule_entries = tuple(rules)
    if not all(isinstance(rule, DefaultRule) for rule in rule_entries):
        raise InvalidRuleError("default.invalid_rule", "DEFAULT evaluation accepts only DefaultRule values.")
    if len({rule.rule_id for rule in rule_entries}) != len(rule_entries):
        raise InvalidRuleError("default.duplicate_rule_id", "DEFAULT rule IDs must be unique.")
    known: dict[OpaqueId, Support] = {}
    for support in supports:
        if not isinstance(support, (DirectSupport, DerivedSupport, DefaultSupport)):
            raise InvalidRuleError("default.invalid_support", "DEFAULT evaluation accepts only recognized supports.")
        if support.support_id in known:
            raise InvalidRuleError("default.duplicate_support_id", "Support IDs must be unique.")
        known[support.support_id] = support
    ordinary = tuple(
        known[key] for key in sorted(known, key=lambda item: item.value)
        if isinstance(known[key], (DirectSupport, DerivedSupport))
    )
    for rule in sorted(rule_entries, key=lambda item: item.rule_id.value):
        for bindings, premises in _match_premises(rule.premises, ordinary):
            if not evaluate_guard(rule.guard, bindings):
                continue
            proposition = _instantiate(rule.conclusion, bindings)
            premise_ids = tuple(sorted((item.support_id for item in premises), key=lambda item: item.value))
            support_id = _support_id(rule, proposition, premise_ids)
            if support_id not in known:
                known[support_id] = DefaultSupport(support_id, proposition, rule.conclusion_polarity, rule.rule_id, premise_ids)
    return tuple(known[key] for key in sorted(known, key=lambda item: item.value))


def _match_premises(premises: tuple[SupportPattern, ...], supports: tuple[Support, ...]) -> tuple[tuple[Bindings, tuple[Support, ...]], ...]:
    matches: list[tuple[Bindings, tuple[Support, ...]]] = [({}, ())]
    for premise in premises:
        next_matches: list[tuple[Bindings, tuple[Support, ...]]] = []
        for bindings, matched in matches:
            for support in supports:
                resolved = match_support(premise, support, bindings)
                if resolved is not None:
                    next_matches.append((resolved, (*matched, support)))
        matches = next_matches
    return tuple(matches)


def _instantiate(pattern: PropositionPattern, bindings: Mapping[Variable, KernelArgument]) -> Proposition:
    return pattern.relation.apply(*(bindings[item] if isinstance(item, Variable) else item for item in pattern.arguments))


def _support_id(rule: DefaultRule, proposition: Proposition, premise_ids: tuple[OpaqueId, ...]) -> OpaqueId:
    payload = repr((rule.rule_id.value, rule.conclusion_polarity.name, proposition.relation.name, tuple(kind.name for kind in proposition.relation.argument_kinds), tuple((type(item).__name__, repr(item.value)) for item in proposition.arguments), tuple(item.value for item in premise_ids)))
    return OpaqueId(f"default-{hashlib.sha256(payload.encode('utf-8')).hexdigest()}")
