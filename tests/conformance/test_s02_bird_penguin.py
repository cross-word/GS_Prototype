from worldkernel import (
    ArgumentKind,
    DefaultRule,
    DefaultSupport,
    DeriveRule,
    DirectSupport,
    EffectiveStatus,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    default_is_defeated,
    derive_closure,
    effective_status,
    evaluate_defaults,
)


def test_s02_default_is_defeated_but_retained_in_provenance() -> None:
    penguin = RelationSchema("Penguin", (ArgumentKind.ID,))
    bird = RelationSchema("Bird", (ArgumentKind.ID,))
    can_fly = RelationSchema("CanFly", (ArgumentKind.ID,))
    subject = Variable("subject")
    positive_penguin = SupportPattern(
        PropositionPattern(penguin, (subject,)), SupportPolarity.POSITIVE
    )
    derive_rules = (
        DeriveRule(
            OpaqueId("penguin-bird"),
            (positive_penguin,),
            PropositionPattern(bird, (subject,)),
            SupportPolarity.POSITIVE,
        ),
        DeriveRule(
            OpaqueId("penguin-cannot-fly"),
            (positive_penguin,),
            PropositionPattern(can_fly, (subject,)),
            SupportPolarity.NEGATIVE,
        ),
    )
    default_rule = DefaultRule(
        OpaqueId("bird-can-fly"),
        (
            SupportPattern(
                PropositionPattern(bird, (subject,)), SupportPolarity.POSITIVE
            ),
        ),
        PropositionPattern(can_fly, (subject,)),
        SupportPolarity.POSITIVE,
    )
    pingu = OpaqueId("pingu")
    source = DirectSupport(
        OpaqueId("penguin-pingu"),
        penguin.apply(pingu),
        SupportPolarity.POSITIVE,
        "scenario",
    )

    ordinary_supports = derive_closure(derive_rules, (source,))
    supports = evaluate_defaults((default_rule,), ordinary_supports)
    default_support = next(
        item for item in supports if isinstance(item, DefaultSupport)
    )

    assert default_support.proposition == can_fly.apply(pingu)
    assert default_is_defeated(default_support, supports)
    assert effective_status(can_fly.apply(pingu), supports) is EffectiveStatus.FALSE_ONLY
