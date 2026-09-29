import pytest

from worldkernel import AddDirectSupport, EffectiveStatus, OpaqueId, PatchValidationError, SupportPolarity, World, WorldPatch, why
from worldmodel import CONCEPT, ENTITY, INSTANCE_OF, concepts_of, create_entity, define_concept, labels_of, standard_world_runtime


def test_s106_unknown_membership_remains_open_world_unknown() -> None:
    kiki, bird = OpaqueId("kiki"), OpaqueId("bird")
    world = World.empty(OpaqueId("world")).commit(create_entity(OpaqueId("kiki-edit"), kiki))
    world = world.commit(define_concept(OpaqueId("bird-edit"), bird))
    snapshot = standard_world_runtime().evaluate(world)

    assert snapshot.effective_status(INSTANCE_OF.apply(kiki, bird)) is EffectiveStatus.UNKNOWN


def test_s111_labels_do_not_merge_distinct_ids() -> None:
    left, right = OpaqueId("western-dragon"), OpaqueId("constellation-dragon")
    world = World.empty(OpaqueId("world")).commit(define_concept(OpaqueId("left"), left, labels=("Dragon",)))
    world = world.commit(define_concept(OpaqueId("right"), right, labels=("Dragon",)))
    snapshot = standard_world_runtime().evaluate(world)

    assert left != right
    assert labels_of(snapshot, left) == labels_of(snapshot, right) == ("Dragon",)


def test_s113_s114_queries_use_derived_view_with_standard_rule_provenance() -> None:
    animal, bear, bruno = OpaqueId("animal"), OpaqueId("bear"), OpaqueId("bruno")
    world = World.empty(OpaqueId("world")).commit(define_concept(OpaqueId("animal-edit"), animal))
    world = world.commit(define_concept(OpaqueId("bear-edit"), bear, parent_concepts=(animal,)))
    world = world.commit(create_entity(OpaqueId("bruno-edit"), bruno, concepts=(bear,)))
    snapshot = standard_world_runtime().evaluate(world)
    graph = why(INSTANCE_OF.apply(bruno, animal), snapshot.supports)

    assert concepts_of(snapshot, bruno) == (animal, bear)
    assert OpaqueId("swm.rule.instance_inheritance") in {node.rule_id for node in graph.nodes}


def test_s115_invalid_multi_operation_patch_leaves_world_unchanged() -> None:
    item = OpaqueId("item")
    world = World.empty(OpaqueId("world"))
    valid = AddDirectSupport(OpaqueId("concept"), CONCEPT.apply(item), SupportPolarity.POSITIVE, "test")
    invalid = AddDirectSupport(OpaqueId("bad"), ENTITY.apply(item), "not-polarity", "test")
    patch = WorldPatch(OpaqueId("atomic"), (valid, invalid), "test")

    with pytest.raises(PatchValidationError):
        world.commit(patch)
    assert world.current.supports == ()
