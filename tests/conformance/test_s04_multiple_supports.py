from worldkernel import (
    ArgumentKind,
    DeriveRule,
    DerivedSupport,
    DirectSupport,
    EffectiveStatus,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    derive_closure,
    effective_status,
    retract_support,
)


def test_s04_retracting_one_path_preserves_the_other() -> None:
    bird = RelationSchema("Bird", (ArgumentKind.ID,))
    penguin = RelationSchema("Penguin", (ArgumentKind.ID,))
    animal = RelationSchema("Animal", (ArgumentKind.ID,))
    subject = Variable("subject")
    rules = (
        DeriveRule(
            OpaqueId("bird-animal"),
            (SupportPattern(PropositionPattern(bird, (subject,)), SupportPolarity.POSITIVE),),
            PropositionPattern(animal, (subject,)),
            SupportPolarity.POSITIVE,
        ),
        DeriveRule(
            OpaqueId("penguin-animal"),
            (SupportPattern(PropositionPattern(penguin, (subject,)), SupportPolarity.POSITIVE),),
            PropositionPattern(animal, (subject,)),
            SupportPolarity.POSITIVE,
        ),
    )
    toto = OpaqueId("toto")
    bird_support = DirectSupport(
        OpaqueId("bird-toto"), bird.apply(toto), SupportPolarity.POSITIVE, "scenario"
    )
    penguin_support = DirectSupport(
        OpaqueId("penguin-toto"), penguin.apply(toto), SupportPolarity.POSITIVE, "scenario"
    )

    closure = derive_closure(rules, (bird_support, penguin_support))
    animal_supports = tuple(
        item
        for item in closure
        if isinstance(item, DerivedSupport) and item.proposition == animal.apply(toto)
    )
    retracted = retract_support(closure, bird_support.support_id)

    assert len(animal_supports) == 2
    assert effective_status(animal.apply(toto), retracted) is EffectiveStatus.TRUE_ONLY
    assert all(
        bird_support.support_id not in item.premise_support_ids
        for item in retracted
        if isinstance(item, DerivedSupport)
    )
