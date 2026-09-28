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
    why,
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


def test_why_marks_a_defeated_default_without_removing_its_justification() -> None:
    schema = RelationSchema("Marked", (ArgumentKind.ID,))
    proposition = schema.apply(OpaqueId("item"))
    default = DefaultSupport(
        OpaqueId("default"), proposition, SupportPolarity.POSITIVE, OpaqueId("rule"), (OpaqueId("premise"),)
    )
    contrary = DirectSupport(OpaqueId("contrary"), proposition, SupportPolarity.NEGATIVE, "test")

    graph = why(proposition, (default, contrary))

    assert next(node for node in graph.nodes if node.support_id == default.support_id).default_is_defeated is True
