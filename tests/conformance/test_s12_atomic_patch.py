import pytest

from worldkernel import (
    AddDirectSupport,
    ArgumentKind,
    OpaqueId,
    PatchValidationError,
    RelationSchema,
    SupportPolarity,
    World,
    WorldPatch,
)


def test_s12_invalid_patch_leaves_world_and_revision_history_unchanged() -> None:
    creature = RelationSchema("Creature", (ArgumentKind.ID,))
    world = World.empty(OpaqueId("world"))
    patch = WorldPatch(
        OpaqueId("patch"),
        (
            AddDirectSupport(OpaqueId("valid"), creature.apply(OpaqueId("kiki")), SupportPolarity.POSITIVE, "player"),
            AddDirectSupport(OpaqueId("invalid"), "not-a-proposition", SupportPolarity.POSITIVE, "player"),
        ),
        "player",
    )

    with pytest.raises(PatchValidationError) as error:
        world.commit(patch)

    assert error.value.details["operation_index"] == 1
    assert world.current.supports == ()
    assert len(world.revisions) == 1
