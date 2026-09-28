from worldkernel import (
    ArgumentKind,
    DefaultRule,
    DefaultSupport,
    DirectSupport,
    EffectiveStatus,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    default_is_defeated,
    effective_status,
    evaluate_defaults,
)


def test_conflicting_defaults_are_preserved_as_a_conflict() -> None:
    seed = RelationSchema("Seed", (ArgumentKind.ID,))
    outcome = RelationSchema("Outcome", (ArgumentKind.ID,))
    subject = Variable("subject")
    premise = SupportPattern(
        PropositionPattern(seed, (subject,)), SupportPolarity.POSITIVE
    )
    rules = (
        DefaultRule(
            OpaqueId("default-positive"),
            (premise,),
            PropositionPattern(outcome, (subject,)),
            SupportPolarity.POSITIVE,
        ),
        DefaultRule(
            OpaqueId("default-negative"),
            (premise,),
            PropositionPattern(outcome, (subject,)),
            SupportPolarity.NEGATIVE,
        ),
    )
    source = DirectSupport(
        OpaqueId("seed-item"),
        seed.apply(OpaqueId("item")),
        SupportPolarity.POSITIVE,
        "test",
    )

    supports = evaluate_defaults(rules, (source,))
    defaults = tuple(item for item in supports if isinstance(item, DefaultSupport))

    assert len(defaults) == 2
    assert not any(default_is_defeated(item, supports) for item in defaults)
    assert effective_status(outcome.apply(OpaqueId("item")), supports) is EffectiveStatus.CONFLICT
