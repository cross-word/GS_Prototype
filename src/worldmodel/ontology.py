"""Inspectable P1 ontology inference expressed as P0 DERIVE rules."""

from collections.abc import Iterable

from worldkernel import DefaultRule, DeriveRule, OpaqueId, PropositionPattern, SemanticRuntime, SupportPattern, SupportPolarity, TriggerRule, Variable

from .vocabulary import INSTANCE_OF, SUBTYPE_OF


def standard_ontology_rules() -> tuple[DeriveRule, ...]:
    subtype, parent, subject = Variable("subtype"), Variable("parent"), Variable("subject")
    ancestor = Variable("ancestor")
    positive_subtype = lambda left, right: SupportPattern(PropositionPattern(SUBTYPE_OF, (left, right)), SupportPolarity.POSITIVE)
    return (
        DeriveRule(OpaqueId("swm.rule.subtype_transitivity"), (positive_subtype(subtype, parent), positive_subtype(parent, ancestor)), PropositionPattern(SUBTYPE_OF, (subtype, ancestor)), SupportPolarity.POSITIVE),
        DeriveRule(OpaqueId("swm.rule.instance_inheritance"), (SupportPattern(PropositionPattern(INSTANCE_OF, (subject, subtype)), SupportPolarity.POSITIVE), positive_subtype(subtype, parent)), PropositionPattern(INSTANCE_OF, (subject, parent)), SupportPolarity.POSITIVE),
    )


def standard_world_rules() -> tuple[DeriveRule, ...]:
    return standard_ontology_rules()


def standard_world_runtime(*, derive_rules: Iterable[DeriveRule] = (), default_rules: Iterable[DefaultRule] = (), trigger_rules: Iterable[TriggerRule] = ()) -> SemanticRuntime:
    """Compose P1 inference with caller-supplied P0 rules without forking runtime."""
    return SemanticRuntime((*standard_world_rules(), *tuple(derive_rules)), tuple(default_rules), tuple(trigger_rules))
