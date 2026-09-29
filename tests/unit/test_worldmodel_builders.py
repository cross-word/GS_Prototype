from worldkernel import OpaqueId
from worldmodel import define_concept


def test_concept_builder_returns_a_deterministic_atomic_patch() -> None:
    patch = define_concept(OpaqueId("edit"), OpaqueId("animal"), labels=("Zoo", "Animal"), source="player")
    assert patch.source == "player"
    assert len(patch.operations) == 3
    assert tuple(operation.support_id for operation in patch.operations) == tuple(operation.support_id for operation in define_concept(OpaqueId("edit"), OpaqueId("animal"), labels=("Animal", "Zoo"), source="player").operations)
