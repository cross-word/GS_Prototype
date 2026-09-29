from worldkernel import OpaqueId, SemanticRuntime, World
from worldmodel import add_related, define_relation, related_objects, relations_between


def test_s110_dynamic_binary_relation_is_world_data() -> None:
    parent, alice, bob = OpaqueId("parent-of"), OpaqueId("alice"), OpaqueId("bob")
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_relation(OpaqueId("define-parent"), parent, labels=("ParentOf",)))
    world = world.commit(add_related(OpaqueId("alice-bob"), parent, alice, bob))
    snapshot = SemanticRuntime().evaluate(world)

    assert related_objects(snapshot, parent, alice) == (bob,)
    assert relations_between(snapshot, alice, bob) == (parent,)
