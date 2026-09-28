from dataclasses import FrozenInstanceError

import pytest

from worldkernel import (
    ArgumentKind,
    BooleanValue,
    InvalidRelationSchemaError,
    MalformedPropositionError,
    NumberValue,
    OpaqueId,
    Proposition,
    RelationSchema,
    StringValue,
)


def test_relation_schema_exposes_stable_name_and_arity() -> None:
    health = RelationSchema(
        name="Health",
        argument_kinds=(ArgumentKind.ID, ArgumentKind.NUMBER),
    )

    assert health.name == "Health"
    assert health.arity == 2


@pytest.mark.parametrize("name", ["", 10, None])
def test_relation_schema_rejects_invalid_names(name: object) -> None:
    with pytest.raises(InvalidRelationSchemaError) as error:
        RelationSchema(name=name, argument_kinds=())  # type: ignore[arg-type]

    assert error.value.code == "relation.invalid_name"


def test_relation_schema_rejects_unknown_argument_kinds() -> None:
    with pytest.raises(InvalidRelationSchemaError) as error:
        RelationSchema(
            name="Health",
            argument_kinds=(ArgumentKind.ID, "Number"),  # type: ignore[arg-type]
        )

    assert error.value.code == "relation.invalid_argument_kind"
    assert error.value.details["index"] == 1


def test_relation_applies_to_well_formed_arguments() -> None:
    description = RelationSchema(
        name="Description",
        argument_kinds=(
            ArgumentKind.ID,
            ArgumentKind.STRING,
            ArgumentKind.BOOLEAN,
            ArgumentKind.NUMBER,
        ),
    )

    proposition = description.apply(
        OpaqueId("bear"),
        StringValue("four wings"),
        BooleanValue(True),
        NumberValue(4),
    )

    assert proposition == Proposition(
        relation=description,
        arguments=(
            OpaqueId("bear"),
            StringValue("four wings"),
            BooleanValue(True),
            NumberValue(4),
        ),
    )
    assert hash(proposition) == hash(description.apply(*proposition.arguments))


def test_proposition_rejects_wrong_arity_with_structured_error() -> None:
    parent_of = RelationSchema(
        name="ParentOf",
        argument_kinds=(ArgumentKind.ID, ArgumentKind.ID),
    )

    with pytest.raises(MalformedPropositionError) as error:
        parent_of.apply(OpaqueId("alice"))

    assert error.value.code == "proposition.arity_mismatch"
    assert error.value.details == {
        "relation": "ParentOf",
        "expected_arity": 2,
        "actual_arity": 1,
    }


def test_proposition_rejects_wrong_argument_kind_with_structured_error() -> None:
    health = RelationSchema(
        name="Health",
        argument_kinds=(ArgumentKind.ID, ArgumentKind.NUMBER),
    )

    with pytest.raises(MalformedPropositionError) as error:
        health.apply(OpaqueId("rabbit"), StringValue("ten"))

    assert error.value.code == "proposition.argument_kind_mismatch"
    assert error.value.details["relation"] == "Health"
    assert error.value.details["index"] == 1
    assert error.value.details["expected_kind"] == "NUMBER"
    assert error.value.details["actual_type"] == "StringValue"


def test_proposition_is_immutable_hashable_and_has_no_truth_field() -> None:
    can_fly = RelationSchema("CanFly", (ArgumentKind.ID,))
    proposition = can_fly.apply(OpaqueId("pingu"))

    assert proposition in {proposition}
    assert not hasattr(proposition, "is_true")
    assert not hasattr(proposition, "status")

    with pytest.raises(FrozenInstanceError):
        proposition.arguments = ()  # type: ignore[misc]

