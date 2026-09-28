"""P0.4 monotonic DERIVE rule evaluation."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .errors import DerivationLimitError, InvalidRuleError
from .expressions import Expression, evaluate_guard, expression_variables
from .model import KernelArgument, OpaqueId, Proposition
from .pattern import Bindings, PropositionPattern, SupportPattern, Variable, match_support
from .support import DirectSupport, DerivedSupport, Support, SupportPolarity


@dataclass(frozen=True, slots=True)
class DeriveRule:
    """A monotonic rule that produces one explicitly polarized support."""

    rule_id: OpaqueId
    premises: tuple[SupportPattern, ...]
    conclusion: PropositionPattern
    conclusion_polarity: SupportPolarity
    guard: Expression | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.rule_id, OpaqueId):
            raise InvalidRuleError(
                code="derive.invalid_rule_id",
                message="A DERIVE rule must have an opaque rule ID.",
                details={"actual_type": type(self.rule_id).__name__},
            )
        try:
            premise_entries = tuple(self.premises)
        except TypeError as error:
            raise InvalidRuleError(
                code="derive.invalid_premises",
                message="DERIVE premises must be iterable support patterns.",
                details={"actual_type": type(self.premises).__name__},
            ) from error
        if not premise_entries or not all(
            isinstance(premise, SupportPattern) for premise in premise_entries
        ):
            raise InvalidRuleError(
                code="derive.invalid_premises",
                message="A DERIVE rule must contain one or more support patterns.",
                details={},
            )
        if not isinstance(self.conclusion, PropositionPattern):
            raise InvalidRuleError(
                code="derive.invalid_conclusion",
                message="A DERIVE rule conclusion must be a proposition pattern.",
                details={"actual_type": type(self.conclusion).__name__},
            )
        if not isinstance(self.conclusion_polarity, SupportPolarity):
            raise InvalidRuleError(
                code="derive.invalid_conclusion_polarity",
                message="A DERIVE rule must use a recognized conclusion polarity.",
                details={"actual_type": type(self.conclusion_polarity).__name__},
            )

        premise_variables = {
            argument
            for premise in premise_entries
            for argument in premise.proposition.arguments
            if isinstance(argument, Variable)
        }
        unbound = sorted(
            {
                argument.name
                for argument in self.conclusion.arguments
                if isinstance(argument, Variable) and argument not in premise_variables
            }
        )
        if unbound:
            raise InvalidRuleError(
                code="derive.unbound_conclusion_variable",
                message="Every conclusion variable must be bound by a premise.",
                details={"variables": unbound},
            )
        if self.guard is not None and not expression_variables(self.guard) <= premise_variables:
            raise InvalidRuleError("derive.unbound_guard_variable", "Every DERIVE guard variable must be bound by a premise.")
        object.__setattr__(self, "premises", premise_entries)


def derive_closure(
    rules: Iterable[DeriveRule],
    supports: Iterable[Support],
    *,
    max_iterations: int = 1000,
) -> tuple[Support, ...]:
    """Return direct and derived support at a deterministic DERIVE fixed point."""

    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations < 1:
        raise InvalidRuleError(
            code="derive.invalid_max_iterations",
            message="The DERIVE iteration limit must be a positive integer.",
            details={"max_iterations": max_iterations},
        )
    rule_entries = _validated_rules(rules)
    known = _index_supports(supports)

    for _ in range(max_iterations):
        additions: dict[OpaqueId, DerivedSupport] = {}
        ordered_supports = tuple(known[key] for key in sorted(known, key=lambda item: item.value))
        for rule in rule_entries:
            for bindings, premises in _match_premises(rule.premises, ordered_supports):
                if not evaluate_guard(rule.guard, bindings):
                    continue
                proposition = _instantiate(rule.conclusion, bindings)
                if _would_form_cycle(
                    proposition, rule.conclusion_polarity, premises, known
                ):
                    continue
                premise_ids = tuple(
                    sorted(
                        (support.support_id for support in premises),
                        key=lambda item: item.value,
                    )
                )
                support_id = _derived_support_id(rule, proposition, premise_ids)
                if support_id in known or support_id in additions:
                    continue
                additions[support_id] = DerivedSupport(
                    support_id=support_id,
                    proposition=proposition,
                    polarity=rule.conclusion_polarity,
                    rule_id=rule.rule_id,
                    premise_support_ids=premise_ids,
                )
        if not additions:
            return tuple(known[key] for key in sorted(known, key=lambda item: item.value))
        known.update(additions)

    raise DerivationLimitError(
        f"DERIVE closure exceeded its iteration limit of {max_iterations}."
    )


def _validated_rules(rules: Iterable[DeriveRule]) -> tuple[DeriveRule, ...]:
    try:
        entries = tuple(rules)
    except TypeError as error:
        raise InvalidRuleError(
            code="derive.invalid_rules",
            message="DERIVE rules must be iterable.",
            details={"actual_type": type(rules).__name__},
        ) from error
    if not all(isinstance(rule, DeriveRule) for rule in entries):
        raise InvalidRuleError(
            code="derive.invalid_rule",
            message="DERIVE evaluation accepts only DeriveRule values.",
            details={},
        )
    rule_ids = [rule.rule_id for rule in entries]
    if len(set(rule_ids)) != len(rule_ids):
        raise InvalidRuleError(
            code="derive.duplicate_rule_id",
            message="DERIVE rule IDs must be unique within one evaluation.",
            details={},
        )
    return tuple(sorted(entries, key=lambda rule: rule.rule_id.value))


def _index_supports(supports: Iterable[Support]) -> dict[OpaqueId, Support]:
    try:
        entries = tuple(supports)
    except TypeError as error:
        raise InvalidRuleError(
            code="derive.invalid_supports",
            message="DERIVE supports must be iterable.",
            details={"actual_type": type(supports).__name__},
        ) from error
    result: dict[OpaqueId, Support] = {}
    for support in entries:
        if not isinstance(support, (DirectSupport, DerivedSupport)):
            raise InvalidRuleError(
                code="derive.invalid_support",
                message="DERIVE evaluation accepts only recognized support values.",
                details={"actual_type": type(support).__name__},
            )
        if support.support_id in result:
            raise InvalidRuleError(
                code="derive.duplicate_support_id",
                message="Support IDs must be unique within one evaluation.",
                details={"support_id": support.support_id.value},
            )
        result[support.support_id] = support
    return result


def _match_premises(
    premises: tuple[SupportPattern, ...], supports: tuple[Support, ...]
) -> tuple[tuple[Bindings, tuple[Support, ...]], ...]:
    matches: list[tuple[Bindings, tuple[Support, ...]]] = [({}, ())]
    for premise in premises:
        next_matches: list[tuple[Bindings, tuple[Support, ...]]] = []
        for bindings, matched_supports in matches:
            for support in supports:
                resolved = match_support(premise, support, bindings)
                if resolved is not None:
                    next_matches.append((resolved, (*matched_supports, support)))
        matches = next_matches
    return tuple(matches)


def _instantiate(
    pattern: PropositionPattern, bindings: Mapping[Variable, KernelArgument]
) -> Proposition:
    arguments: list[KernelArgument] = []
    for argument in pattern.arguments:
        if isinstance(argument, Variable):
            try:
                arguments.append(bindings[argument])
            except KeyError as error:
                raise InvalidRuleError(
                    code="derive.unbound_conclusion_variable",
                    message="A conclusion variable was not bound during matching.",
                    details={"variable": argument.name},
                ) from error
        else:
            arguments.append(argument)
    return pattern.relation.apply(*arguments)


def _would_form_cycle(
    proposition: Proposition,
    polarity: SupportPolarity,
    premises: tuple[Support, ...],
    known: Mapping[OpaqueId, Support],
) -> bool:
    target = (proposition, polarity)
    return any(target in _support_ancestry(premise, known) for premise in premises)


def _support_ancestry(
    support: Support, known: Mapping[OpaqueId, Support]
) -> set[tuple[Proposition, SupportPolarity]]:
    ancestry = {(support.proposition, support.polarity)}
    if isinstance(support, DerivedSupport):
        for premise_id in support.premise_support_ids:
            premise = known.get(premise_id)
            if premise is not None:
                ancestry.update(_support_ancestry(premise, known))
    return ancestry


def _derived_support_id(
    rule: DeriveRule,
    proposition: Proposition,
    premise_ids: tuple[OpaqueId, ...],
) -> OpaqueId:
    payload = repr(
        (
            rule.rule_id.value,
            rule.conclusion_polarity.name,
            proposition.relation.name,
            tuple(kind.name for kind in proposition.relation.argument_kinds),
            tuple((type(argument).__name__, repr(argument.value)) for argument in proposition.arguments),
            tuple(item.value for item in premise_ids),
        )
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return OpaqueId(f"derived-{digest}")
