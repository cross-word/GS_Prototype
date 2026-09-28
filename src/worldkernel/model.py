"""Domain-neutral value objects for the P0.1 Meta-Kernel vocabulary."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

from .errors import (
    InvalidIdError,
    InvalidRelationSchemaError,
    InvalidScalarValueError,
    MalformedPropositionError,
)


@dataclass(frozen=True, slots=True)
class OpaqueId:
    """An opaque runtime identity with stable value equality."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise InvalidIdError(
                code="id.invalid_value",
                message="An opaque ID must contain a non-empty string.",
                details={"value": self.value},
            )

    def __str__(self) -> str:
        return f"@{self.value}"

    def __repr__(self) -> str:
        return f"OpaqueId({self.value!r})"


@dataclass(frozen=True, slots=True)
class NumberValue:
    """A finite P0 numeric scalar."""

    value: int | float

    def __post_init__(self) -> None:
        is_number = isinstance(self.value, (int, float)) and not isinstance(
            self.value, bool
        )
        is_finite = not isinstance(self.value, float) or math.isfinite(self.value)
        if not is_number or not is_finite:
            raise InvalidScalarValueError(
                code="value.invalid_number",
                message="A Number value must be a finite int or float, excluding bool.",
                details={"value": self.value},
            )


@dataclass(frozen=True, slots=True)
class BooleanValue:
    """A P0 boolean scalar."""

    value: bool

    def __post_init__(self) -> None:
        if not isinstance(self.value, bool):
            raise InvalidScalarValueError(
                code="value.invalid_boolean",
                message="A Boolean value must contain a bool.",
                details={"value": self.value},
            )


@dataclass(frozen=True, slots=True)
class StringValue:
    """A P0 string scalar."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidScalarValueError(
                code="value.invalid_string",
                message="A String value must contain a str.",
                details={"value": self.value},
            )


ScalarValue: TypeAlias = NumberValue | BooleanValue | StringValue
KernelArgument: TypeAlias = OpaqueId | ScalarValue


class ArgumentKind(Enum):
    """P0 argument categories understood by relation schemas."""

    ID = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()


_ARGUMENT_TYPES: dict[ArgumentKind, type[KernelArgument]] = {
    ArgumentKind.ID: OpaqueId,
    ArgumentKind.NUMBER: NumberValue,
    ArgumentKind.BOOLEAN: BooleanValue,
    ArgumentKind.STRING: StringValue,
}


@dataclass(frozen=True, slots=True)
class RelationSchema:
    """A named n-ary relation with minimal argument-kind constraints."""

    name: str
    argument_kinds: tuple[ArgumentKind, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise InvalidRelationSchemaError(
                code="relation.invalid_name",
                message="A relation name must be a non-empty string.",
                details={"name": self.name},
            )

        try:
            canonical_kinds = tuple(self.argument_kinds)
        except TypeError as error:
            raise InvalidRelationSchemaError(
                code="relation.invalid_argument_kinds",
                message="Relation argument kinds must be an iterable of ArgumentKind values.",
                details={"argument_kinds": self.argument_kinds},
            ) from error

        for index, kind in enumerate(canonical_kinds):
            if not isinstance(kind, ArgumentKind):
                raise InvalidRelationSchemaError(
                    code="relation.invalid_argument_kind",
                    message="A relation argument kind is not recognized.",
                    details={"index": index, "argument_kind": kind},
                )

        object.__setattr__(self, "argument_kinds", canonical_kinds)

    @property
    def arity(self) -> int:
        return len(self.argument_kinds)

    def apply(self, *arguments: KernelArgument) -> Proposition:
        return Proposition(relation=self, arguments=arguments)


@dataclass(frozen=True, slots=True)
class Proposition:
    """An immutable, well-formed relation application with no truth field."""

    relation: RelationSchema
    arguments: tuple[KernelArgument, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.relation, RelationSchema):
            raise MalformedPropositionError(
                code="proposition.invalid_relation",
                message="A proposition must reference a RelationSchema.",
                details={"actual_type": type(self.relation).__name__},
            )

        try:
            canonical_arguments = tuple(self.arguments)
        except TypeError as error:
            raise MalformedPropositionError(
                code="proposition.invalid_arguments",
                message="Proposition arguments must be iterable.",
                details={"actual_type": type(self.arguments).__name__},
            ) from error

        if len(canonical_arguments) != self.relation.arity:
            raise MalformedPropositionError(
                code="proposition.arity_mismatch",
                message="Proposition argument count does not match relation arity.",
                details={
                    "relation": self.relation.name,
                    "expected_arity": self.relation.arity,
                    "actual_arity": len(canonical_arguments),
                },
            )

        for index, (expected_kind, argument) in enumerate(
            zip(self.relation.argument_kinds, canonical_arguments, strict=True)
        ):
            expected_type = _ARGUMENT_TYPES[expected_kind]
            if not isinstance(argument, expected_type):
                raise MalformedPropositionError(
                    code="proposition.argument_kind_mismatch",
                    message="A proposition argument does not match its relation schema.",
                    details={
                        "relation": self.relation.name,
                        "index": index,
                        "expected_kind": expected_kind.name,
                        "actual_type": type(argument).__name__,
                    },
                )

        object.__setattr__(self, "arguments", canonical_arguments)

