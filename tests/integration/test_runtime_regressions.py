from worldkernel import (
    AddDirectSupport, ArgumentKind, DefaultRule, DeriveRule, DirectSupport,
    NumberValue, OpaqueId, PropositionPattern, RelationSchema, SemanticRuntime,
    SupportPattern, SupportPolarity, TriggerAdd, TriggerRule, Variable, World,
    WorldPatch, derive_closure,
)


def _world(schema: RelationSchema, item: OpaqueId) -> World:
    return World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("setup"), (AddDirectSupport(OpaqueId("source"), schema.apply(item), SupportPolarity.POSITIVE, "test"),), "test"))


def test_defeated_default_does_not_activate_a_trigger() -> None:
    bird, fly, observed = (RelationSchema(name, (ArgumentKind.ID,)) for name in ("Bird", "Fly", "Observed"))
    x = Variable("x")
    runtime = SemanticRuntime((), (DefaultRule(OpaqueId("bird-fly"), (SupportPattern(PropositionPattern(bird, (x,)), SupportPolarity.POSITIVE),), PropositionPattern(fly, (x,)), SupportPolarity.POSITIVE),), (TriggerRule(OpaqueId("observe-fly"), (SupportPattern(PropositionPattern(fly, (x,)), SupportPolarity.POSITIVE),), (TriggerAdd(PropositionPattern(observed, (x,)), SupportPolarity.POSITIVE),)),))
    item = OpaqueId("item")
    world = _world(bird, item).commit(WorldPatch(OpaqueId("contrary"), (AddDirectSupport(OpaqueId("cannot-fly"), fly.apply(item), SupportPolarity.NEGATIVE, "test"),), "test"))
    assert runtime.run_trigger_phase(world) == world


def test_trigger_outputs_are_deduplicated_and_repeated_firing_is_idempotent() -> None:
    pair = RelationSchema("Pair", (ArgumentKind.ID, ArgumentKind.ID)); alert = RelationSchema("Alert", (ArgumentKind.ID,)); x, y = Variable("x"), Variable("y")
    runtime = SemanticRuntime((), (), (TriggerRule(OpaqueId("alert"), (SupportPattern(PropositionPattern(pair, (x, y)), SupportPolarity.POSITIVE),), (TriggerAdd(PropositionPattern(alert, (x,)), SupportPolarity.POSITIVE),)),))
    world = World.empty(OpaqueId("world")).commit(WorldPatch(OpaqueId("setup"), (AddDirectSupport(OpaqueId("one"), pair.apply(OpaqueId("a"), OpaqueId("b")), SupportPolarity.POSITIVE, "test"), AddDirectSupport(OpaqueId("two"), pair.apply(OpaqueId("a"), OpaqueId("c")), SupportPolarity.POSITIVE, "test")), "test"))
    first = runtime.run_trigger_phase(world)
    assert len([support for support in first.current.supports if support.proposition == alert.apply(OpaqueId("a"))]) == 1
    assert runtime.run_trigger_phase(first) == first


def test_numeric_equivalent_values_produce_the_same_derived_identity() -> None:
    measured, result = RelationSchema("Measured", (ArgumentKind.NUMBER,)), RelationSchema("Result", (ArgumentKind.NUMBER,))
    x = Variable("x")
    rule = DeriveRule(OpaqueId("copy"), (SupportPattern(PropositionPattern(measured, (x,)), SupportPolarity.POSITIVE),), PropositionPattern(result, (x,)), SupportPolarity.POSITIVE)
    one = derive_closure((rule,), (DirectSupport(OpaqueId("one"), measured.apply(NumberValue(1)), SupportPolarity.POSITIVE, "test"),))[-1]
    float_one = derive_closure((rule,), (DirectSupport(OpaqueId("one"), measured.apply(NumberValue(1.0)), SupportPolarity.POSITIVE, "test"),))[-1]
    assert one.support_id == float_one.support_id


def test_runtime_output_is_deterministic_when_rule_and_support_orders_reverse() -> None:
    seed, left, right = (RelationSchema(name, (ArgumentKind.ID,)) for name in ("Seed", "Left", "Right"))
    x = Variable("x"); premise = SupportPattern(PropositionPattern(seed, (x,)), SupportPolarity.POSITIVE)
    rules = (DeriveRule(OpaqueId("left"), (premise,), PropositionPattern(left, (x,)), SupportPolarity.POSITIVE), DeriveRule(OpaqueId("right"), (premise,), PropositionPattern(right, (x,)), SupportPolarity.POSITIVE))
    supports = (DirectSupport(OpaqueId("a"), seed.apply(OpaqueId("a")), SupportPolarity.POSITIVE, "test"), DirectSupport(OpaqueId("b"), seed.apply(OpaqueId("b")), SupportPolarity.POSITIVE, "test"))
    assert derive_closure(rules, supports) == derive_closure(tuple(reversed(rules)), tuple(reversed(supports)))
