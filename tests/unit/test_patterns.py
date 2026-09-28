from dataclasses import FrozenInstanceError

import pytest

from worldkernel import (
    ArgumentKind,
    DirectSupport,
    InvalidPatternError,
    InvalidVariableError,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    match_conjunction,
    match_proposition,
    match_support,
)


def test_variable_is_immutable_and_rejects_an_empty_name() -> None:
    variable = Variable("subject")

    assert variable == Variable("subject")
    with pytest.raises(FrozenInstanceError):
        variable.name = "other"  # type: ignore[misc]
    with pytest.raises(InvalidVariableError) as error:
        Variable("")

    assert error.value.code == "variable.invalid_name"


def test_proposition_pattern_binds_variables_and_fixed_arguments() -> None:
    parent_of = RelationSchema("ParentOf", (ArgumentKind.ID, ArgumentKind.ID))
    subject = Variable("subject")
    pattern = PropositionPattern(parent_of, (subject, OpaqueId("bob")))

    bindings = match_proposition(
        pattern,
        parent_of.apply(OpaqueId("alice"), OpaqueId("bob")),
    )

    assert bindings == {subject: OpaqueId("alice")}


def test_repeated_variable_requires_the_same_value() -> None:
    same_as = RelationSchema("SameAs", (ArgumentKind.ID, ArgumentKind.ID))
    subject = Variable("subject")
    pattern = PropositionPattern(same_as, (subject, subject))

    assert match_proposition(
        pattern,
        same_as.apply(OpaqueId("alice"), OpaqueId("alice")),
    ) == {subject: OpaqueId("alice")}
    assert (
        match_proposition(
            pattern,
            same_as.apply(OpaqueId("alice"), OpaqueId("bob")),
        )
        is None
    )


def test_proposition_pattern_rejects_malformed_fixed_arguments() -> None:
    health = RelationSchema("Health", (ArgumentKind.ID, ArgumentKind.NUMBER))

    with pytest.raises(InvalidPatternError) as error:
        PropositionPattern(health, (OpaqueId("rabbit"), OpaqueId("ten")))

    assert error.value.code == "pattern.argument_kind_mismatch"


def test_support_pattern_requires_the_requested_polarity() -> None:
    dragon = RelationSchema("Dragon", (ArgumentKind.ID,))
    subject = Variable("subject")
    pattern = SupportPattern(
        proposition=PropositionPattern(dragon, (subject,)),
        polarity=SupportPolarity.NEGATIVE,
    )
    negative = DirectSupport(
        support_id=OpaqueId("support-1"),
        proposition=dragon.apply(OpaqueId("smaug")),
        polarity=SupportPolarity.NEGATIVE,
        origin="test",
    )
    positive = DirectSupport(
        support_id=OpaqueId("support-2"),
        proposition=dragon.apply(OpaqueId("smaug")),
        polarity=SupportPolarity.POSITIVE,
        origin="test",
    )

    assert match_support(pattern, negative) == {subject: OpaqueId("smaug")}
    assert match_support(pattern, positive) is None


def test_conjunctive_matching_returns_consistent_bindings_in_stable_order() -> None:
    owns = RelationSchema("Owns", (ArgumentKind.ID, ArgumentKind.ID))
    painted = RelationSchema("Painted", (ArgumentKind.ID,))
    person = Variable("person")
    item = Variable("item")
    patterns = (
        PropositionPattern(owns, (person, item)),
        PropositionPattern(painted, (item,)),
    )
    propositions = {
        owns.apply(OpaqueId("zoe"), OpaqueId("canvas")),
        painted.apply(OpaqueId("canvas")),
        owns.apply(OpaqueId("amy"), OpaqueId("mural")),
        painted.apply(OpaqueId("mural")),
    }

    assert match_conjunction(patterns, propositions) == (
        {person: OpaqueId("zoe"), item: OpaqueId("canvas")},
        {person: OpaqueId("amy"), item: OpaqueId("mural")},
    )
