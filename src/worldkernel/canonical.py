"""Small deterministic serialization helpers for semantic identity."""

from __future__ import annotations

from decimal import Decimal

from .model import BooleanValue, KernelArgument, NumberValue, OpaqueId, Proposition, StringValue


def canonical_argument(argument: KernelArgument) -> tuple[str, str]:
    if isinstance(argument, OpaqueId):
        return ("id", argument.value)
    if isinstance(argument, NumberValue):
        return ("number", _number(argument.value))
    if isinstance(argument, BooleanValue):
        return ("boolean", "true" if argument.value else "false")
    if isinstance(argument, StringValue):
        return ("string", argument.value)
    raise TypeError(f"Unsupported kernel argument: {type(argument).__name__}")


def canonical_proposition(proposition: Proposition) -> tuple[str, tuple[str, ...], tuple[tuple[str, str], ...]]:
    return (
        proposition.relation.name,
        tuple(kind.name for kind in proposition.relation.argument_kinds),
        tuple(canonical_argument(argument) for argument in proposition.arguments),
    )


def _number(value: int | float) -> str:
    decimal = Decimal(str(value)).normalize()
    return "0" if decimal == 0 else format(decimal, "f")
