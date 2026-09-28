from worldkernel import AddDirectSupport, ArgumentKind, OpaqueId, RelationSchema, SupportPolarity, World, WorldPatch


def test_commit_creates_one_child_revision_with_all_valid_operations() -> None:
    marker = RelationSchema("Marker", (ArgumentKind.ID,))
    world = World.empty(OpaqueId("world"))
    patch = WorldPatch(OpaqueId("patch"), (AddDirectSupport(OpaqueId("positive"), marker.apply(OpaqueId("item")), SupportPolarity.POSITIVE, "player"),), "player")

    updated = world.commit(patch)

    assert updated.current.parent_revision_id == world.current.revision_id
    assert len(updated.current.supports) == 1
    assert world.current.supports == ()
