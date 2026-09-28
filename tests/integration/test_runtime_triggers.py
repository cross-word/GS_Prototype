from worldkernel import AddDirectSupport, ArgumentKind, DefaultRule, DeriveRule, OpaqueId, PropositionPattern, RelationSchema, SemanticRuntime, SupportPattern, SupportPolarity, TriggerAdd, TriggerRule, Variable, World, WorldPatch

def test_derived_support_is_visible_to_trigger() -> None:
    penguin = RelationSchema("Penguin", (ArgumentKind.ID,)); bird = RelationSchema("Bird", (ArgumentKind.ID,)); observed = RelationSchema("Observed", (ArgumentKind.ID,)); x = Variable("x")
    runtime = SemanticRuntime((DeriveRule(OpaqueId("p-b"), (SupportPattern(PropositionPattern(penguin, (x,)), SupportPolarity.POSITIVE),), PropositionPattern(bird, (x,)), SupportPolarity.POSITIVE),), (), (TriggerRule(OpaqueId("observe"), (SupportPattern(PropositionPattern(bird, (x,)), SupportPolarity.POSITIVE),), (TriggerAdd(PropositionPattern(observed, (x,)), SupportPolarity.POSITIVE),)),))
    world = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("setup"), (AddDirectSupport(OpaqueId("pingu"), penguin.apply(OpaqueId("pingu")), SupportPolarity.POSITIVE, "test"),), "test"))
    updated = runtime.run_trigger_phase(world)
    assert any(item.proposition == observed.apply(OpaqueId("pingu")) for item in updated.current.supports)
