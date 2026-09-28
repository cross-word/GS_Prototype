from worldkernel import ArgumentKind, OpaqueId, RelationSchema


def test_s01_fixture_can_represent_the_required_propositions_without_truth() -> None:
    creature = RelationSchema("Creature", (ArgumentKind.ID,))
    has_wing = RelationSchema("HasWing", (ArgumentKind.ID,))
    can_fly = RelationSchema("CanFly", (ArgumentKind.ID,))
    kiki = OpaqueId("kiki")

    given = {creature.apply(kiki), has_wing.apply(kiki)}
    unknown_candidate = can_fly.apply(kiki)

    assert {proposition.relation.name for proposition in given} == {
        "Creature",
        "HasWing",
    }
    assert unknown_candidate not in given
    assert not hasattr(unknown_candidate, "status")

