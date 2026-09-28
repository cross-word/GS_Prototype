from worldkernel import (
    ArgumentKind,
    EffectiveStatus,
    OpaqueId,
    RelationSchema,
    effective_status,
)


def test_s01_unknown_creature_is_not_negative_support() -> None:
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
    assert effective_status(unknown_candidate, ()) is EffectiveStatus.UNKNOWN
