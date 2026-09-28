from worldkernel import ArgumentKind, NumberValue, OpaqueId, RelationSchema, canonical_proposition


def test_numerically_equal_values_have_identical_canonical_propositions() -> None:
    health = RelationSchema("Health", (ArgumentKind.ID, ArgumentKind.NUMBER))

    assert health.apply(OpaqueId("rabbit"), NumberValue(1)) == health.apply(
        OpaqueId("rabbit"), NumberValue(1.0)
    )
    assert canonical_proposition(health.apply(OpaqueId("rabbit"), NumberValue(1))) == canonical_proposition(
        health.apply(OpaqueId("rabbit"), NumberValue(1.0))
    )
