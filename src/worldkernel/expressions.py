"""P0.10's small, typed, deterministic expression language for rule guards."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from collections.abc import Mapping
from typing import TypeAlias

from .errors import InvalidExpressionError
from .model import BooleanValue, KernelArgument, NumberValue, StringValue, OpaqueId
from .pattern import Variable


class UnaryOperator(Enum):
    NOT = auto()
    NEGATE = auto()


class BinaryOperator(Enum):
    AND = auto()
    OR = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()


@dataclass(frozen=True, slots=True)
class Literal:
    value: KernelArgument

    def __post_init__(self) -> None:
        if not isinstance(self.value, (OpaqueId, NumberValue, BooleanValue, StringValue)):
            raise InvalidExpressionError("expression.invalid_literal", "An expression literal must be a kernel argument.")


@dataclass(frozen=True, slots=True)
class VariableReference:
    variable: Variable

    def __post_init__(self) -> None:
        if not isinstance(self.variable, Variable):
            raise InvalidExpressionError("expression.invalid_variable", "An expression variable reference requires a Variable.")


@dataclass(frozen=True, slots=True)
class UnaryExpression:
    operator: UnaryOperator
    operand: Expression

    def __post_init__(self) -> None:
        if not isinstance(self.operator, UnaryOperator) or not isinstance(self.operand, (Literal, VariableReference, UnaryExpression, BinaryExpression)):
            raise InvalidExpressionError("expression.invalid_unary", "A unary expression has an operator and expression operand.")


@dataclass(frozen=True, slots=True)
class BinaryExpression:
    operator: BinaryOperator
    left: Expression
    right: Expression

    def __post_init__(self) -> None:
        if not isinstance(self.operator, BinaryOperator) or not isinstance(self.left, (Literal, VariableReference, UnaryExpression, BinaryExpression)) or not isinstance(self.right, (Literal, VariableReference, UnaryExpression, BinaryExpression)):
            raise InvalidExpressionError("expression.invalid_binary", "A binary expression has an operator and expression operands.")


Expression: TypeAlias = Literal | VariableReference | UnaryExpression | BinaryExpression


def expression_variables(expression: Expression) -> frozenset[Variable]:
    if isinstance(expression, VariableReference):
        return frozenset((expression.variable,))
    if isinstance(expression, Literal):
        return frozenset()
    if isinstance(expression, UnaryExpression):
        return expression_variables(expression.operand)
    if isinstance(expression, BinaryExpression):
        return expression_variables(expression.left) | expression_variables(expression.right)
    raise InvalidExpressionError("expression.invalid", "Expected a recognized expression.")


def evaluate_expression(expression: Expression, bindings: Mapping[Variable, KernelArgument]) -> object:
    """Evaluate a guard expression without host-language evaluation or coercion."""
    if isinstance(expression, Literal):
        return _unwrap(expression.value)
    if isinstance(expression, VariableReference):
        try:
            return _unwrap(bindings[expression.variable])
        except KeyError as error:
            raise InvalidExpressionError("expression.unbound_variable", "Guard evaluation referenced an unbound variable.", {"variable": expression.variable.name}) from error
    if isinstance(expression, UnaryExpression):
        value = evaluate_expression(expression.operand, bindings)
        if expression.operator is UnaryOperator.NOT:
            return not _boolean(value)
        if expression.operator is UnaryOperator.NEGATE:
            return -_number(value)
    if isinstance(expression, BinaryExpression):
        left = evaluate_expression(expression.left, bindings)
        right = evaluate_expression(expression.right, bindings)
        operator = expression.operator
        if operator is BinaryOperator.AND: return _boolean(left) and _boolean(right)
        if operator is BinaryOperator.OR: return _boolean(left) or _boolean(right)
        if operator is BinaryOperator.EQUAL: return _semantic_equal(left, right)
        if operator is BinaryOperator.NOT_EQUAL: return not _semantic_equal(left, right)
        if operator is BinaryOperator.LESS_THAN: return _number(left) < _number(right)
        if operator is BinaryOperator.LESS_THAN_OR_EQUAL: return _number(left) <= _number(right)
        if operator is BinaryOperator.GREATER_THAN: return _number(left) > _number(right)
        if operator is BinaryOperator.GREATER_THAN_OR_EQUAL: return _number(left) >= _number(right)
        if operator is BinaryOperator.ADD: return _number(left) + _number(right)
        if operator is BinaryOperator.SUBTRACT: return _number(left) - _number(right)
        if operator is BinaryOperator.MULTIPLY: return _number(left) * _number(right)
        if operator is BinaryOperator.DIVIDE:
            divisor = _number(right)
            if divisor == 0: raise InvalidExpressionError("expression.divide_by_zero", "Division by zero is invalid in P0 expressions.")
            return _number(left) / divisor
    raise InvalidExpressionError("expression.invalid", "Expected a recognized expression.")


def evaluate_guard(guard: Expression | None, bindings: Mapping[Variable, KernelArgument]) -> bool:
    if guard is None:
        return True
    value = evaluate_expression(guard, bindings)
    return _boolean(value)


def _unwrap(value: KernelArgument) -> object:
    return value if isinstance(value, OpaqueId) else value.value


def _number(value: object) -> int | float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InvalidExpressionError("expression.invalid_numeric_operand", "Arithmetic and ordering require numeric operands.")
    return value


def _boolean(value: object) -> bool:
    if not isinstance(value, bool):
        raise InvalidExpressionError("expression.invalid_boolean_operand", "A guard and logical operator require boolean operands.")
    return value


def _semantic_equal(left: object, right: object) -> bool:
    """Apply the P0 scalar equality policy without Python bool/int coercion."""
    if _is_number(left) and _is_number(right):
        return left == right
    return type(left) is type(right) and left == right


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
