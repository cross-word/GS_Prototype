from worldkernel import AddDirectSupport, ArgumentKind, OpaqueId, PropositionPattern, RelationSchema, RemoveDirectSupport, SupportPattern, SupportPolarity, TriggerRule, TriggerAdd, Variable, World, WorldPatch, run_trigger_phase

def test_s05_trigger_patch_persists_after_condition_removal() -> None:
    glass = RelationSchema("Glass", (ArgumentKind.ID,)); collision = RelationSchema("Collision", (ArgumentKind.ID, ArgumentKind.ID)); broken = RelationSchema("Broken", (ArgumentKind.ID,))
    cup = OpaqueId("cup"); ground = OpaqueId("ground"); world = World.empty(OpaqueId("world"))
    world = world.commit(WorldPatch(OpaqueId("setup"), (AddDirectSupport(OpaqueId("glass"), glass.apply(cup), SupportPolarity.POSITIVE, "test"), AddDirectSupport(OpaqueId("collision"), collision.apply(cup, ground), SupportPolarity.POSITIVE, "test")), "test"))
    item = Variable("item")
    rule = TriggerRule(OpaqueId("break"), (SupportPattern(PropositionPattern(collision, (item, ground)), SupportPolarity.POSITIVE), SupportPattern(PropositionPattern(glass, (item,)), SupportPolarity.POSITIVE)), (TriggerAdd(PropositionPattern(broken, (item,)), SupportPolarity.POSITIVE),))
    triggered = run_trigger_phase(world, (rule,))
    assert any(item.proposition == broken.apply(cup) for item in triggered.current.supports)
    after_removal = triggered.commit(WorldPatch(OpaqueId("remove-collision"), (RemoveDirectSupport(OpaqueId("collision")),), "test"))
    assert any(item.proposition == broken.apply(cup) for item in after_removal.current.supports)
