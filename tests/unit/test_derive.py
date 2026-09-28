import pytest

from worldkernel import (
    ArgumentKind,
    DeriveRule,
    DerivedSupport,
    DirectSupport,
    InvalidRuleError,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    derive_closure,
)


def test_derive_rule_rejects_an_unbound_conclusion_variable() -> None:
    source = RelationSchema("Source", (ArgumentKind.ID,))
    target = RelationSchema("Target", (ArgumentKind.ID,))

    with pytest.raises(InvalidRuleError) as error:
        DeriveRule(
            rule_id=OpaqueId("invalid"),
            premises=(
                SupportPattern(
                    PropositionPattern(source, (Variable("source"),)),
                    SupportPolarity.POSITIVE,
                ),
            ),
            conclusion=PropositionPattern(target, (Variable("target"),)),
            conclusion_polarity=SupportPolarity.POSITIVE,
        )

    assert error.value.code == "derive.unbound_conclusion_variable"


def test_derive_closure_records_rule_and_premise_provenance() -> None:
    bird = RelationSchema("Bird", (ArgumentKind.ID,))
    animal = RelationSchema("Animal", (ArgumentKind.ID,))
    subject = Variable("subject")
    rule = DeriveRule(
        rule_id=OpaqueId("bird-to-animal"),
        premises=(
            SupportPattern(
                PropositionPattern(bird, (subject,)),
                SupportPolarity.POSITIVE,
            ),
        ),
        conclusion=PropositionPattern(animal, (subject,)),
        conclusion_polarity=SupportPolarity.POSITIVE,
    )
    source = DirectSupport(
        support_id=OpaqueId("bird-toto"),
        proposition=bird.apply(OpaqueId("toto")),
        polarity=SupportPolarity.POSITIVE,
        origin="test",
    )

    supports = derive_closure((rule,), (source,))
    derived = next(support for support in supports if isinstance(support, DerivedSupport))

    assert derived.proposition == animal.apply(OpaqueId("toto"))
    assert derived.polarity is SupportPolarity.POSITIVE
    assert derived.rule_id == rule.rule_id
    assert derived.premise_support_ids == (source.support_id,)


def test_derive_closure_suppresses_self_referential_cycles() -> None:
    marker = RelationSchema("Marker", (ArgumentKind.ID,))
    subject = Variable("subject")
    positive_marker = SupportPattern(
        PropositionPattern(marker, (subject,)),
        SupportPolarity.POSITIVE,
    )
    rules = (
        DeriveRule(
            OpaqueId("first"),
            (positive_marker,),
            PropositionPattern(marker, (subject,)),
            SupportPolarity.POSITIVE,
        ),
        DeriveRule(
            OpaqueId("second"),
            (positive_marker,),
            PropositionPattern(marker, (subject,)),
            SupportPolarity.POSITIVE,
        ),
    )
    source = DirectSupport(
        OpaqueId("marker-source"),
        marker.apply(OpaqueId("item")),
        SupportPolarity.POSITIVE,
        "test",
    )

    supports = derive_closure(rules, (source,))
    derived = tuple(support for support in supports if isinstance(support, DerivedSupport))

    assert derived == ()
