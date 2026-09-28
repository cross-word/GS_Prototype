import pytest

from worldkernel import (
    ArgumentKind,
    BinaryExpression,
    BinaryOperator,
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
