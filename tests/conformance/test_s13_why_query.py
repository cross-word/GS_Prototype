from worldkernel import ArgumentKind, DeriveRule, DirectSupport, OpaqueId, PropositionPattern, RelationSchema, SupportPattern, SupportPolarity, Variable, derive_closure, why

def test_s13_why_query_returns_a_two_step_justification_graph() -> None:
    penguin = RelationSchema("Penguin", (ArgumentKind.ID,)); bird = RelationSchema("Bird", (ArgumentKind.ID,)); animal = RelationSchema("Animal", (ArgumentKind.ID,)); subject = Variable("subject")
    rules = (DeriveRule(OpaqueId("penguin-bird"), (SupportPattern(PropositionPattern(penguin, (subject,)), SupportPolarity.POSITIVE),), PropositionPattern(bird, (subject,)), SupportPolarity.POSITIVE), DeriveRule(OpaqueId("bird-animal"), (SupportPattern(PropositionPattern(bird, (subject,)), SupportPolarity.POSITIVE),), PropositionPattern(animal, (subject,)), SupportPolarity.POSITIVE))
    source = DirectSupport(OpaqueId("penguin-pingu"), penguin.apply(OpaqueId("pingu")), SupportPolarity.POSITIVE, "player")
    graph = why(animal.apply(OpaqueId("pingu")), derive_closure(rules, (source,)), OpaqueId("revision-1"))
    assert {node.rule_id for node in graph.nodes if node.rule_id} == {OpaqueId("penguin-bird"), OpaqueId("bird-animal")}
    assert source.support_id in {node.support_id for node in graph.nodes}
    assert graph.queried_at_revision_id == OpaqueId("revision-1")
    assert all(node.originating_revision_id is None for node in graph.nodes)
    assert next(node for node in graph.nodes if node.support_id == source.support_id).origin == "player"
