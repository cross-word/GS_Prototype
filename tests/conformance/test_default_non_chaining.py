from worldkernel import (
    ArgumentKind,
    DefaultRule,
    DirectSupport,
    OpaqueId,
    PropositionPattern,
    RelationSchema,
    SupportPattern,
    SupportPolarity,
    Variable,
    evaluate_defaults,
)


def test_default_conclusions_do_not_chain_into_other_default_premises() -> None:
    seed = RelationSchema("Seed", (ArgumentKind.ID,))
    middle = RelationSchema("Middle", (ArgumentKind.ID,))
    outcome = RelationSchema("Outcome", (ArgumentKind.ID,))
    subject = Variable("subject")
    positive_seed = SupportPattern(PropositionPattern(seed, (subject,)), SupportPolarity.POSITIVE)
    positive_middle = SupportPattern(PropositionPattern(middle, (subject,)), SupportPolarity.POSITIVE)
    rules = (
        DefaultRule(OpaqueId("seed-middle"), (positive_seed,), PropositionPattern(middle, (subject,)), SupportPolarity.POSITIVE),
        DefaultRule(OpaqueId("middle-outcome"), (positive_middle,), PropositionPattern(outcome, (subject,)), SupportPolarity.POSITIVE),
    )
    item = OpaqueId("item")
    source = DirectSupport(OpaqueId("seed-item"), seed.apply(item), SupportPolarity.POSITIVE, "test")

    supports = evaluate_defaults(rules, (source,))

    assert any(entry.proposition == middle.apply(item) for entry in supports)
    assert not any(entry.proposition == outcome.apply(item) for entry in supports)
