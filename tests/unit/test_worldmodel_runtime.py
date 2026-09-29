from worldkernel import OpaqueId, World
from worldmodel import concepts_of, create_entity, define_concept, standard_world_runtime


def test_standard_runtime_exposes_inherited_membership_in_its_snapshot() -> None:
    animal, bear, bruno = OpaqueId("animal"), OpaqueId("bear"), OpaqueId("bruno")
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_concept(OpaqueId("animal-patch"), animal))
    world = world.commit(define_concept(OpaqueId("bear-patch"), bear, parent_concepts=(animal,)))
    world = world.commit(create_entity(OpaqueId("bruno-patch"), bruno, concepts=(bear,)))

    assert concepts_of(standard_world_runtime().evaluate(world), bruno) == (animal, bear)
