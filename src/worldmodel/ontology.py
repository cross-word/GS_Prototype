"""Inspectable P1 ontology inference expressed as P0 DERIVE rules."""

from worldkernel import DeriveRule, OpaqueId, PropositionPattern, SupportPattern, SupportPolarity, Variable

from .vocabulary import INSTANCE_OF, SUBTYPE_OF


def standard_ontology_rules() -> tuple[DeriveRule, ...]:
    subtype, parent, subject = Variable("subtype"), Variable("parent"), Variable("subject")
    ancestor = Variable("ancestor")
    positive_subtype = lambda left, right: SupportPattern(PropositionPattern(SUBTYPE_OF, (left, right)), SupportPolarity.POSITIVE)
    return (
        DeriveRule(OpaqueId("swm.rule.subtype_transitivity"), (positive_subtype(subtype, parent), positive_subtype(parent, ancestor)), PropositionPattern(SUBTYPE_OF, (subtype, ancestor)), SupportPolarity.POSITIVE),
        DeriveRule(OpaqueId("swm.rule.instance_inheritance"), (SupportPattern(PropositionPattern(INSTANCE_OF, (subject, subtype)), SupportPolarity.POSITIVE), positive_subtype(subtype, parent)), PropositionPattern(INSTANCE_OF, (subject, parent)), SupportPolarity.POSITIVE),
    )
