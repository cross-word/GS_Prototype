import pytest

from worldkernel import (
    ArgumentKind, BinaryExpression, BinaryOperator, InvalidRuleError, Literal,
    NumberValue, OpaqueId, PropositionPattern, RelationSchema, SupportPattern,
    SupportPolarity, TriggerAdd, TriggerRule, Variable, VariableReference,
)


def _premise(variable: Variable) -> SupportPattern:
    return SupportPattern(PropositionPattern(RelationSchema("Source", (ArgumentKind.ID,)), (variable,)), SupportPolarity.POSITIVE)


def _output(variable: Variable) -> TriggerAdd:
    return TriggerAdd(PropositionPattern(RelationSchema("Outcome", (ArgumentKind.ID,)), (variable,)), SupportPolarity.POSITIVE)


@pytest.mark.parametrize(
    ("rule_id", "premises", "outputs", "code"),
    (
        ("not-id", (), (), "trigger.invalid_rule_id"),
        (OpaqueId("rule"), (), (), "trigger.invalid_premises"),
        (OpaqueId("rule"), ("not-premise",), (), "trigger.invalid_premises"),
        (OpaqueId("rule"), (_premise(Variable("x")),), (), "trigger.invalid_outputs"),
        (OpaqueId("rule"), (_premise(Variable("x")),), ("not-output",), "trigger.invalid_outputs"),
    ),
)
def test_trigger_rule_rejects_malformed_structure(rule_id, premises, outputs, code) -> None:
    with pytest.raises(InvalidRuleError) as error:
        TriggerRule(rule_id, premises, outputs)
    assert error.value.code == code


def test_trigger_rule_rejects_unbound_output_and_guard_variables() -> None:
    x, y = Variable("x"), Variable("y")
    with pytest.raises(InvalidRuleError, match="output") as output_error:
        TriggerRule(OpaqueId("output"), (_premise(x),), (_output(y),))
    assert output_error.value.code == "trigger.unbound_output_variable"
    with pytest.raises(InvalidRuleError, match="guard") as guard_error:
        TriggerRule(OpaqueId("guard"), (_premise(x),), (_output(x),), BinaryExpression(BinaryOperator.EQUAL, VariableReference(y), Literal(NumberValue(1))))
    assert guard_error.value.code == "trigger.unbound_guard_variable"
