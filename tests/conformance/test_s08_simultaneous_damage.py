from worldkernel import AddDirectSupport, ArgumentKind, OpaqueId, PropositionPattern, RelationSchema, SemanticRuntime, SupportPattern, SupportPolarity, TriggerAdd, TriggerRule, Variable, World, WorldPatch

def test_s08_trigger_outputs_are_not_visible_until_the_next_phase() -> None:
    source = RelationSchema("Source", (ArgumentKind.ID,)); intermediate = RelationSchema("Intermediate", (ArgumentKind.ID,)); final = RelationSchema("Final", (ArgumentKind.ID,)); x = Variable("x")
    runtime = SemanticRuntime(trigger_rules=(TriggerRule(OpaqueId("first"), (SupportPattern(PropositionPattern(source, (x,)), SupportPolarity.POSITIVE),), (TriggerAdd(PropositionPattern(intermediate, (x,)), SupportPolarity.POSITIVE),)), TriggerRule(OpaqueId("second"), (SupportPattern(PropositionPattern(intermediate, (x,)), SupportPolarity.POSITIVE),), (TriggerAdd(PropositionPattern(final, (x,)), SupportPolarity.POSITIVE),))))
    world = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("setup"), (AddDirectSupport(OpaqueId("source"), source.apply(OpaqueId("a")), SupportPolarity.POSITIVE, "test"),), "test"))
    first = runtime.run_trigger_phase(world)
    assert any(item.proposition == intermediate.apply(OpaqueId("a")) for item in first.current.supports)
    assert not any(item.proposition == final.apply(OpaqueId("a")) for item in first.current.supports)
    second = runtime.run_trigger_phase(first)
    assert any(item.proposition == final.apply(OpaqueId("a")) for item in second.current.supports)
