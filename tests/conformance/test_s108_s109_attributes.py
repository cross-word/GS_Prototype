from worldkernel import OpaqueId, SemanticRuntime, World
from worldmodel import add_number_attribute, add_string_attribute, define_attribute, number_attribute_values, string_attribute_values


def test_s108_s109_typed_attributes_are_dynamic_and_multi_valued() -> None:
    health, color, bruno, alice = (OpaqueId(value) for value in ("health", "color", "bruno", "alice"))
    world = World.empty(OpaqueId("world"))
    world = world.commit(define_attribute(OpaqueId("health-def"), health, labels=("Health",)))
    world = world.commit(define_attribute(OpaqueId("color-def"), color))
    world = world.commit(add_number_attribute(OpaqueId("health-value"), bruno, health, 80))
    world = world.commit(add_string_attribute(OpaqueId("red"), alice, color, "red"))
    world = world.commit(add_string_attribute(OpaqueId("blue"), alice, color, "blue"))
    snapshot = SemanticRuntime().evaluate(world)

    assert number_attribute_values(snapshot, bruno, health) == (80,)
    assert string_attribute_values(snapshot, alice, color) == ("blue", "red")
