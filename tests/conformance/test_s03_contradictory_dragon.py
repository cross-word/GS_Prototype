from worldkernel import (
    ArgumentKind,
    DeriveRule,
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
)


def test_s03_contradiction_propagates_without_unrelated_conclusions() -> None:
    dragon = RelationSchema("Dragon", (ArgumentKind.ID,))
    mortal = RelationSchema("Mortal", (ArgumentKind.ID,))
    finite_life = RelationSchema("HasFiniteLife", (ArgumentKind.ID,))
    eternal = RelationSchema("Eternal", (ArgumentKind.ID,))
    unrelated = RelationSchema("Unrelated", (ArgumentKind.ID,))
    subject = Variable("subject")
    positive_dragon = SupportPattern(
        PropositionPattern(dragon, (subject,)),
        SupportPolarity.POSITIVE,
    )
    positive_mortal = SupportPattern(
        PropositionPattern(mortal, (subject,)),
        SupportPolarity.POSITIVE,
    )
    negative_mortal = SupportPattern(
        PropositionPattern(mortal, (subject,)),
        SupportPolarity.NEGATIVE,
    )
    rules = (
        DeriveRule(OpaqueId("dragon-mortal-positive"), (positive_dragon,), PropositionPattern(mortal, (subject,)), SupportPolarity.POSITIVE),
        DeriveRule(OpaqueId("dragon-mortal-negative"), (positive_dragon,), PropositionPattern(mortal, (subject,)), SupportPolarity.NEGATIVE),
        DeriveRule(OpaqueId("mortal-finite"), (positive_mortal,), PropositionPattern(finite_life, (subject,)), SupportPolarity.POSITIVE),
        DeriveRule(OpaqueId("mortal-eternal"), (negative_mortal,), PropositionPattern(eternal, (subject,)), SupportPolarity.POSITIVE),
    )
    smaug = OpaqueId("smaug")
    source = DirectSupport(OpaqueId("dragon-smaug"), dragon.apply(smaug), SupportPolarity.POSITIVE, "scenario")

    supports = derive_closure(rules, (source,))

    assert effective_status(mortal.apply(smaug), supports) is EffectiveStatus.CONFLICT
    assert effective_status(finite_life.apply(smaug), supports) is EffectiveStatus.TRUE_ONLY
    assert effective_status(eternal.apply(smaug), supports) is EffectiveStatus.TRUE_ONLY
    assert effective_status(unrelated.apply(smaug), supports) is EffectiveStatus.UNKNOWN
