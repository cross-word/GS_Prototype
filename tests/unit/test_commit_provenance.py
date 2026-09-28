from worldkernel import AddDirectSupport, ArgumentKind, OpaqueId, RelationSchema, SupportPolarity, World, WorldPatch


def test_revision_identity_includes_committed_semantic_content_and_record() -> None:
    marker = RelationSchema("Marker", (ArgumentKind.ID,))
    parent = World.empty(OpaqueId("world"))
    first = parent.commit(WorldPatch(OpaqueId("patch"), (AddDirectSupport(OpaqueId("support"), marker.apply(OpaqueId("one")), SupportPolarity.POSITIVE, "player"),), "player"))
    second = parent.commit(WorldPatch(OpaqueId("patch"), (AddDirectSupport(OpaqueId("support"), marker.apply(OpaqueId("two")), SupportPolarity.POSITIVE, "player"),), "player"))

    assert first.current.revision_id != second.current.revision_id
    assert first.current.commit_record.patch_id == OpaqueId("patch")
    assert first.current.commit_record.source == "player"
    assert first.current.commit_record.operations[0].support_id == OpaqueId("support")
