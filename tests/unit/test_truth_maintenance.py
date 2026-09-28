from worldkernel import (
    ArgumentKind,
    DeriveRule,
    DerivedSupport,
    DirectSupport,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    derive_closure,
    retract_support,
)


def test_retraction_propagates_through_a_derived_chain() -> None:
    source = RelationSchema("Source", (ArgumentKind.ID,))
    middle = RelationSchema("Middle", (ArgumentKind.ID,))
    target = RelationSchema("Target", (ArgumentKind.ID,))
    subject = Variable("subject")
    rules = (
        DeriveRule(
            OpaqueId("source-middle"),
            (SupportPattern(PropositionPattern(source, (subject,)), SupportPolarity.POSITIVE),),
            PropositionPattern(middle, (subject,)),
            SupportPolarity.POSITIVE,
        ),
        DeriveRule(
            OpaqueId("middle-target"),
            (SupportPattern(PropositionPattern(middle, (subject,)), SupportPolarity.POSITIVE),),
            PropositionPattern(target, (subject,)),
            SupportPolarity.POSITIVE,
        ),
    )
    direct = DirectSupport(
        OpaqueId("source-item"),
        source.apply(OpaqueId("item")),
        SupportPolarity.POSITIVE,
        "test",
    )

    closure = derive_closure(rules, (direct,))
    remaining = retract_support(closure, direct.support_id)

    assert remaining == ()


def test_distinct_premise_supports_produce_distinct_justification_paths() -> None:
    bird = RelationSchema("Bird", (ArgumentKind.ID,))
    animal = RelationSchema("Animal", (ArgumentKind.ID,))
    subject = Variable("subject")
    rule = DeriveRule(
        OpaqueId("bird-animal"),
        (SupportPattern(PropositionPattern(bird, (subject,)), SupportPolarity.POSITIVE),),
        PropositionPattern(animal, (subject,)),
        SupportPolarity.POSITIVE,
    )
    first = DirectSupport(
        OpaqueId("bird-first"), bird.apply(OpaqueId("toto")), SupportPolarity.POSITIVE, "test"
    )
    second = DirectSupport(
        OpaqueId("bird-second"), bird.apply(OpaqueId("toto")), SupportPolarity.POSITIVE, "test"
    )

    closure = derive_closure((rule,), (first, second))
    derived = tuple(item for item in closure if isinstance(item, DerivedSupport))
    remaining = retract_support(closure, first.support_id)
    remaining_derived = tuple(
        item for item in remaining if isinstance(item, DerivedSupport)
    )

    assert len(derived) == 2
    assert {item.premise_support_ids for item in derived} == {
        (first.support_id,),
        (second.support_id,),
    }
    assert len(remaining_derived) == 1
    assert remaining_derived[0].premise_support_ids == (second.support_id,)
