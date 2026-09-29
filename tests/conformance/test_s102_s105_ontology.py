from worldkernel import OpaqueId, SemanticRuntime, World
from worldmodel import concepts_of, create_entity, define_concept, standard_ontology_rules


def test_s102_to_s105_instance_inheritance_transitivity_and_multiple_parents() -> None:
    animal, mammal, flying, bat, bruce = (OpaqueId(value) for value in ("animal", "mammal", "flying", "bat", "bruce"))
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_concept(OpaqueId("animal"), animal))
    world = world.commit(define_concept(OpaqueId("mammal"), mammal, parent_concepts=(animal,)))
    world = world.commit(define_concept(OpaqueId("flying"), flying))
    world = world.commit(define_concept(OpaqueId("bat"), bat, parent_concepts=(mammal, flying)))
    world = world.commit(create_entity(OpaqueId("bruce"), bruce, concepts=(bat,)))
    snapshot = SemanticRuntime(derive_rules=standard_ontology_rules()).evaluate(world)

    assert concepts_of(snapshot, bruce) == (animal, bat, flying, mammal)
