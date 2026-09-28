from worldkernel import (
    AddDirectSupport, ArgumentKind, OpaqueId, PropositionPattern, RelationSchema, RemoveDirectSupport,
    SemanticRuntime, SupportPattern, SupportPolarity, TriggerAdd, TriggerRule,
    Variable, World, WorldPatch, why_in_world,
)


def test_trigger_why_preserves_historical_premises_and_origin_revision() -> None:
    glass, collision, broken = (RelationSchema(name, (ArgumentKind.ID,)) for name in ("Glass", "Collision", "Broken"))
    x = Variable("x")
    rule = TriggerRule(OpaqueId("break"), (
        SupportPattern(PropositionPattern(glass, (x,)), SupportPolarity.POSITIVE),
        SupportPattern(PropositionPattern(collision, (x,)), SupportPolarity.POSITIVE),
    ), (TriggerAdd(PropositionPattern(broken, (x,)), SupportPolarity.POSITIVE),))
    item = OpaqueId("cup")
    world = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("setup"), (
        AddDirectSupport(OpaqueId("glass"), glass.apply(item), SupportPolarity.POSITIVE, "player"),
        AddDirectSupport(OpaqueId("collision"), collision.apply(item), SupportPolarity.POSITIVE, "player"),
    ), "player"))
    triggered = SemanticRuntime((), (), (rule,)).run_trigger_phase(world)
    trigger_revision = triggered.current.revision_id
    updated = triggered.commit(WorldPatch(OpaqueId("remove-collision"), (RemoveDirectSupport(OpaqueId("collision")),), "player"))

    graph = why_in_world(updated, broken.apply(item))

    result = next(node for node in graph.nodes if node.proposition == broken.apply(item))
    assert result.rule_id == OpaqueId("break")
    assert result.premise_support_ids == (OpaqueId("collision"), OpaqueId("glass"))
    assert result.originating_revision_id == trigger_revision
    assert graph.queried_at_revision_id == updated.current.revision_id
    assert {OpaqueId("glass"), OpaqueId("collision")} <= {node.support_id for node in graph.nodes}


def test_direct_support_keeps_its_first_committed_revision() -> None:
    marker, unrelated = RelationSchema("Marker", (ArgumentKind.ID,)), RelationSchema("Unrelated", (ArgumentKind.ID,))
    item = OpaqueId("item")
    first = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("add"), (AddDirectSupport(OpaqueId("marker"), marker.apply(item), SupportPolarity.POSITIVE, "player"),), "player"))
    second = first.commit(WorldPatch(OpaqueId("other"), (AddDirectSupport(OpaqueId("other"), unrelated.apply(item), SupportPolarity.POSITIVE, "player"),), "player"))

    graph = why_in_world(second, marker.apply(item))

    node = next(node for node in graph.nodes if node.support_id == OpaqueId("marker"))
    assert node.originating_revision_id == first.current.revision_id
    assert graph.queried_at_revision_id == second.current.revision_id
