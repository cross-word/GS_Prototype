"""P0.3 variables and deterministic proposition/support pattern matching."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TypeAlias

from .errors import InvalidPatternError, InvalidVariableError
from .model import (
    ArgumentKind,
    BooleanValue,
    KernelArgument,
    NumberValue,
    OpaqueId,
    Proposition,
    RelationSchema,
    StringValue,
)
from .support import (
    DefaultSupport,
    DirectSupport,
    DerivedSupport,
    Support,
    SupportPolarity,
)


@dataclass(frozen=True, slots=True)
class Variable:
    """A named placeholder that may be bound to one kernel argument."""

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise InvalidVariableError(
                code="variable.invalid_name",
                message="A variable must contain a non-empty string name.",
                details={"name": self.name},
            )


PatternArgument: TypeAlias = KernelArgument | Variable
Bindings: TypeAlias = dict[Variable, KernelArgument]

_ARGUMENT_TYPES: dict[ArgumentKind, type[KernelArgument]] = {
    ArgumentKind.ID: OpaqueId,
    ArgumentKind.NUMBER: NumberValue,
    ArgumentKind.BOOLEAN: BooleanValue,
    ArgumentKind.STRING: StringValue,
}


@dataclass(frozen=True, slots=True)
class PropositionPattern:
    """A relation application whose arguments may include variables."""

    relation: RelationSchema
    arguments: tuple[PatternArgument, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.relation, RelationSchema):
            raise InvalidPatternError(
                code="pattern.invalid_relation",
                message="A proposition pattern must reference a RelationSchema.",
                details={"actual_type": type(self.relation).__name__},
            )
        try:
            canonical_arguments = tuple(self.arguments)
        except TypeError as error:
            raise InvalidPatternError(
                code="pattern.invalid_arguments",
                message="Pattern arguments must be iterable.",
                details={"actual_type": type(self.arguments).__name__},
            ) from error
        if len(canonical_arguments) != self.relation.arity:
            raise InvalidPatternError(
                code="pattern.arity_mismatch",
                message="Pattern argument count does not match relation arity.",
                details={
                    "relation": self.relation.name,
                    "expected_arity": self.relation.arity,
                    "actual_arity": len(canonical_arguments),
                },
            )
        for index, (expected_kind, argument) in enumerate(
            zip(self.relation.argument_kinds, canonical_arguments, strict=True)
        ):
            if isinstance(argument, Variable):
                continue
            if not isinstance(argument, _ARGUMENT_TYPES[expected_kind]):
                raise InvalidPatternError(
                    code="pattern.argument_kind_mismatch",
                    message="A fixed pattern argument does not match its relation schema.",
                    details={
                        "relation": self.relation.name,
                        "index": index,
                        "expected_kind": expected_kind.name,
                        "actual_type": type(argument).__name__,
                    },
                )
        object.__setattr__(self, "arguments", canonical_arguments)


@dataclass(frozen=True, slots=True)
class SupportPattern:
    """A proposition pattern constrained to one explicit support polarity."""

    proposition: PropositionPattern
    polarity: SupportPolarity

    def __post_init__(self) -> None:
        if not isinstance(self.proposition, PropositionPattern):
            raise InvalidPatternError(
                code="pattern.invalid_support_proposition",
                message="A support pattern must contain a proposition pattern.",
                details={"actual_type": type(self.proposition).__name__},
            )
        if not isinstance(self.polarity, SupportPolarity):
            raise InvalidPatternError(
                code="pattern.invalid_support_polarity",
                message="A support pattern must use a recognized polarity.",
                details={"actual_type": type(self.polarity).__name__},
            )


def match_proposition(
    pattern: PropositionPattern,
    proposition: Proposition,
    bindings: Mapping[Variable, KernelArgument] | None = None,
) -> Bindings | None:
    """Match one proposition, returning consistent variable bindings or ``None``."""

    if not isinstance(pattern, PropositionPattern):
        raise InvalidPatternError(
            code="pattern.invalid_query",
            message="A proposition match requires a PropositionPattern.",
            details={"actual_type": type(pattern).__name__},
        )
    if not isinstance(proposition, Proposition):
        raise InvalidPatternError(
            code="pattern.invalid_proposition",
            message="A proposition match requires a well-formed proposition.",
            details={"actual_type": type(proposition).__name__},
        )
    if pattern.relation != proposition.relation:
        return None

    resolved = dict(bindings or {})
    for pattern_argument, proposition_argument in zip(
        pattern.arguments, proposition.arguments, strict=True
    ):
        if isinstance(pattern_argument, Variable):
            existing = resolved.get(pattern_argument)
            if existing is None:
                resolved[pattern_argument] = proposition_argument
            elif existing != proposition_argument:
                return None
        elif pattern_argument != proposition_argument:
            return None
    return resolved


def match_support(
    pattern: SupportPattern,
    support: Support,
    bindings: Mapping[Variable, KernelArgument] | None = None,
) -> Bindings | None:
    """Match a support only when its explicit polarity agrees."""

    if not isinstance(pattern, SupportPattern):
        raise InvalidPatternError(
            code="pattern.invalid_support_query",
            message="A support match requires a SupportPattern.",
            details={"actual_type": type(pattern).__name__},
        )
    if not isinstance(support, (DirectSupport, DerivedSupport, DefaultSupport)):
        raise InvalidPatternError(
            code="pattern.invalid_support",
            message="Support matching requires a recognized support.",
            details={"actual_type": type(support).__name__},
        )
    if pattern.polarity is not support.polarity:
        return None
    return match_proposition(pattern.proposition, support.proposition, bindings)


def match_conjunction(
    patterns: Iterable[PropositionPattern],
    propositions: Iterable[Proposition],
) -> tuple[Bindings, ...]:
    """Match every proposition pattern and return unique bindings in stable order."""

    try:
        pattern_entries = tuple(patterns)
        proposition_entries = tuple(propositions)
    except TypeError as error:
        raise InvalidPatternError(
            code="pattern.invalid_conjunction_entries",
            message="Conjunctive matching requires iterable patterns and propositions.",
            details={},
        ) from error
    for pattern in pattern_entries:
        if not isinstance(pattern, PropositionPattern):
            raise InvalidPatternError(
                code="pattern.invalid_conjunction_pattern",
                message="Conjunctive matching accepts only PropositionPattern entries.",
                details={"actual_type": type(pattern).__name__},
            )
    for proposition in proposition_entries:
        if not isinstance(proposition, Proposition):
            raise InvalidPatternError(
                code="pattern.invalid_conjunction_proposition",
                message="Conjunctive matching accepts only Proposition entries.",
                details={"actual_type": type(proposition).__name__},
            )

    ordered_patterns = tuple(sorted(pattern_entries, key=_pattern_key))
    ordered_propositions = tuple(sorted(proposition_entries, key=_proposition_key))
    matches: list[Bindings] = [{}]
    for pattern in ordered_patterns:
        next_matches: list[Bindings] = []
        for bindings in matches:
            for proposition in ordered_propositions:
                matched = match_proposition(pattern, proposition, bindings)
                if matched is not None:
                    next_matches.append(matched)
        matches = next_matches

    unique_matches = {
        _bindings_key(bindings): bindings
        for bindings in matches
    }
    return tuple(unique_matches[key] for key in sorted(unique_matches))


def _pattern_key(pattern: PropositionPattern) -> tuple[str, tuple[tuple[str, str], ...]]:
    return (
        pattern.relation.name,
        tuple(_pattern_argument_key(argument) for argument in pattern.arguments),
    )


def _proposition_key(proposition: Proposition) -> tuple[str, tuple[tuple[str, str], ...]]:
    return (
        proposition.relation.name,
        tuple(_argument_key(argument) for argument in proposition.arguments),
    )


def _pattern_argument_key(argument: PatternArgument) -> tuple[str, str]:
    if isinstance(argument, Variable):
        return ("variable", argument.name)
    return _argument_key(argument)


def _argument_key(argument: KernelArgument) -> tuple[str, str]:
    return (type(argument).__name__, repr(argument.value))


def _bindings_key(bindings: Mapping[Variable, KernelArgument]) -> tuple[tuple[str, tuple[str, str]], ...]:
    return tuple(
        sorted(
            (variable.name, _argument_key(argument))
            for variable, argument in bindings.items()
        )
    )
