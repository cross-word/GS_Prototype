from worldkernel import OpaqueId, World
from worldmodel import DiagnosticSeverity, define_concept, diagnose_world_model, standard_world_runtime


def test_s112_subtype_cycle_is_representable_and_warned_deterministically() -> None:
    a, b = OpaqueId("a"), OpaqueId("b")
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_concept(OpaqueId("a-edit"), a, parent_concepts=(b,)))
    world = world.commit(define_concept(OpaqueId("b-edit"), b, parent_concepts=(a,)))

    diagnostics = diagnose_world_model(standard_world_runtime().evaluate(world))

    assert len(diagnostics) == 1
    assert diagnostics[0].code == "subtype_cycle"
    assert diagnostics[0].severity is DiagnosticSeverity.WARNING
    assert diagnostics[0].related_ids == (a, b)
