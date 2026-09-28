import pytest

from worldkernel import (
    ArgumentKind,
    BinaryExpression,
    BinaryOperator,
    BooleanValue,
    DeriveRule,
    DirectSupport,
    InvalidExpressionError,
    Literal,
    NumberValue,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    StringValue,
    Variable,
    VariableReference,
    derive_closure,
    evaluate_expression,
)


def test_numeric_guard_filters_a_derive_rule_using_bound_variables() -> None:
    measured = RelationSchema("Measured", (ArgumentKind.ID, ArgumentKind.NUMBER))
    accepted = RelationSchema("Accepted", (ArgumentKind.ID,))
    subject, amount = Variable("subject"), Variable("amount")
    rule = DeriveRule(
        OpaqueId("accept-positive"),
        (SupportPattern(PropositionPattern(measured, (subject, amount)), SupportPolarity.POSITIVE),),
        PropositionPattern(accepted, (subject,)),
        SupportPolarity.POSITIVE,
        BinaryExpression(BinaryOperator.GREATER_THAN, VariableReference(amount), Literal(NumberValue(0))),
    )
    supports = (
        DirectSupport(OpaqueId("positive"), measured.apply(OpaqueId("a"), NumberValue(2)), SupportPolarity.POSITIVE, "test"),
        DirectSupport(OpaqueId("zero"), measured.apply(OpaqueId("b"), NumberValue(0)), SupportPolarity.POSITIVE, "test"),
    )

    closure = derive_closure((rule,), supports)

    assert {entry.proposition for entry in closure if entry.proposition.relation == accepted} == {accepted.apply(OpaqueId("a"))}


def test_expression_rejects_unbound_variables_and_invalid_operands() -> None:
    variable = Variable("value")
    with pytest.raises(InvalidExpressionError, match="unbound"):
        evaluate_expression(VariableReference(variable), {})
    with pytest.raises(InvalidExpressionError, match="numeric"):
        evaluate_expression(BinaryExpression(BinaryOperator.LESS_THAN, Literal(OpaqueId("a")), Literal(OpaqueId("b"))), {})


def test_expression_equality_matches_number_value_semantics() -> None:
    one = Literal(NumberValue(1))
    decimal_one = Literal(NumberValue(1.0))

    assert evaluate_expression(BinaryExpression(BinaryOperator.EQUAL, one, decimal_one), {}) is True
    assert evaluate_expression(BinaryExpression(BinaryOperator.NOT_EQUAL, one, decimal_one), {}) is False
    assert evaluate_expression(BinaryExpression(BinaryOperator.EQUAL, one, Literal(StringValue("1"))), {}) is False
    assert evaluate_expression(BinaryExpression(BinaryOperator.EQUAL, one, Literal(BooleanValue(True))), {}) is False
    assert evaluate_expression(BinaryExpression(BinaryOperator.LESS_THAN, one, Literal(NumberValue(2.0))), {}) is True


def test_numeric_equivalent_guard_accepts_an_integer_binding() -> None:
    measured = RelationSchema("Measured", (ArgumentKind.ID, ArgumentKind.NUMBER))
    accepted = RelationSchema("Accepted", (ArgumentKind.ID,))
    subject, amount = Variable("subject"), Variable("amount")
    rule = DeriveRule(
        OpaqueId("accept-one"),
        (SupportPattern(PropositionPattern(measured, (subject, amount)), SupportPolarity.POSITIVE),),
        PropositionPattern(accepted, (subject,)),
        SupportPolarity.POSITIVE,
        BinaryExpression(BinaryOperator.EQUAL, VariableReference(amount), Literal(NumberValue(1.0))),
    )
    source = DirectSupport(OpaqueId("one"), measured.apply(OpaqueId("a"), NumberValue(1)), SupportPolarity.POSITIVE, "test")

    assert any(entry.proposition == accepted.apply(OpaqueId("a")) for entry in derive_closure((rule,), (source,)))
