from worldkernel import ArgumentKind, DefaultSupport, DirectSupport, OpaqueId, RelationSchema, SemanticSnapshot, SupportPolarity


def test_snapshot_excludes_defeated_defaults_from_active_supports() -> None:
    can_fly = RelationSchema("CanFly", (ArgumentKind.ID,)); proposition = can_fly.apply(OpaqueId("pingu"))
    negative = DirectSupport(OpaqueId("negative"), proposition, SupportPolarity.NEGATIVE, "test")
    default = DefaultSupport(OpaqueId("default"), proposition, SupportPolarity.POSITIVE, OpaqueId("rule"), (OpaqueId("premise"),))
    snapshot = SemanticSnapshot(OpaqueId("revision"), (negative,), (), (default,))
    assert default in snapshot.supports
    assert default not in snapshot.active_supports
    assert negative in snapshot.active_supports
