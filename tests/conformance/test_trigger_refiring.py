from worldkernel import (
    AddDirectSupport, ArgumentKind, OpaqueId, PropositionPattern, RelationSchema,
    RemoveDirectSupport, SemanticRuntime, SupportPattern, SupportPolarity,
    TriggerAdd, TriggerRule, Variable, World, WorldPatch, why_in_world,
)


def test_trigger_refires_with_a_new_occurrence_only_after_prior_effect_is_removed() -> None:
    source, effect, unrelated = (RelationSchema(name, (ArgumentKind.ID,)) for name in ("Source", "Effect", "Unrelated"))
    x = Variable("x")
    runtime = SemanticRuntime(trigger_rules=(TriggerRule(
        OpaqueId("source-effect"),
        (SupportPattern(PropositionPattern(source, (x,)), SupportPolarity.POSITIVE),),
        (TriggerAdd(PropositionPattern(effect, (x,)), SupportPolarity.POSITIVE),),
    ),))
    item = OpaqueId("a")
    initial = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("source"), (AddDirectSupport(OpaqueId("source-a"), source.apply(item), SupportPolarity.POSITIVE, "test"),), "test"))

    phase_one = runtime.run_trigger_phase(initial)
    first_effect = next(support for support in phase_one.current.supports if support.proposition == effect.apply(item))
    unrelated_revision = phase_one.commit(WorldPatch(OpaqueId("unrelated"), (AddDirectSupport(OpaqueId("unrelated-a"), unrelated.apply(item), SupportPolarity.POSITIVE, "test"),), "test"))

    assert runtime.run_trigger_phase(unrelated_revision) == unrelated_revision

    removed = unrelated_revision.commit(WorldPatch(OpaqueId("remove-effect"), (RemoveDirectSupport(first_effect.support_id),), "test"))
    phase_two = runtime.run_trigger_phase(removed)
    second_effect = next(support for support in phase_two.current.supports if support.proposition == effect.apply(item))

    assert second_effect.support_id != first_effect.support_id
    graph = why_in_world(phase_two, effect.apply(item))
    assert next(node for node in graph.nodes if node.support_id == second_effect.support_id).originating_revision_id == phase_two.current.revision_id
