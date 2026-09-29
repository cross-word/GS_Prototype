from worldkernel import OpaqueId, SemanticRuntime, World
from worldmodel import CONCEPT, ENTITY, create_entity, define_concept, labels_of


def test_s101_and_s107_concept_entity_roles_and_labels_are_independent() -> None:
    item = OpaqueId("fire")
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_concept(OpaqueId("concept-edit"), item, labels=("Fire",)))
    world = world.commit(create_entity(OpaqueId("entity-edit"), item, labels=("Fire",)))
    snapshot = SemanticRuntime().evaluate(world)

    assert {support.proposition.relation for support in snapshot.direct_supports} >= {CONCEPT, ENTITY}
    assert labels_of(snapshot, item) == ("Fire",)
