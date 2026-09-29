"""Deterministic P1 queries over evaluated semantic snapshots."""

from worldkernel import OpaqueId, SemanticSnapshot, StringValue, SupportPolarity

from .vocabulary import ATTRIBUTE_BOOLEAN, ATTRIBUTE_NUMBER, ATTRIBUTE_REFERENCE, ATTRIBUTE_STRING, INSTANCE_OF, LABEL


def labels_of(snapshot: SemanticSnapshot, item_id: OpaqueId) -> tuple[str, ...]:
    """Return positively supported labels in deterministic order."""
    return tuple(sorted({support.proposition.arguments[1].value for support in snapshot.active_supports if support.polarity is SupportPolarity.POSITIVE and support.proposition.relation == LABEL and support.proposition.arguments[0] == item_id and isinstance(support.proposition.arguments[1], StringValue)}))


def concepts_of(snapshot: SemanticSnapshot, entity_id: OpaqueId) -> tuple[OpaqueId, ...]:
    return tuple(sorted({support.proposition.arguments[1] for support in snapshot.active_supports if support.polarity is SupportPolarity.POSITIVE and support.proposition.relation == INSTANCE_OF and support.proposition.arguments[0] == entity_id}, key=lambda item: item.value))


def instances_of(snapshot: SemanticSnapshot, concept_id: OpaqueId) -> tuple[OpaqueId, ...]:
    return tuple(sorted({support.proposition.arguments[0] for support in snapshot.active_supports if support.polarity is SupportPolarity.POSITIVE and support.proposition.relation == INSTANCE_OF and support.proposition.arguments[1] == concept_id}, key=lambda item: item.value))


def _attribute_values(snapshot: SemanticSnapshot, relation, item_id: OpaqueId, attribute_id: OpaqueId) -> tuple[object, ...]:
    return tuple(sorted({support.proposition.arguments[2].value for support in snapshot.active_supports if support.polarity is SupportPolarity.POSITIVE and support.proposition.relation == relation and support.proposition.arguments[:2] == (item_id, attribute_id)}, key=repr))


def number_attribute_values(snapshot: SemanticSnapshot, item_id: OpaqueId, attribute_id: OpaqueId) -> tuple[int | float, ...]: return _attribute_values(snapshot, ATTRIBUTE_NUMBER, item_id, attribute_id)
def string_attribute_values(snapshot: SemanticSnapshot, item_id: OpaqueId, attribute_id: OpaqueId) -> tuple[str, ...]: return _attribute_values(snapshot, ATTRIBUTE_STRING, item_id, attribute_id)
def boolean_attribute_values(snapshot: SemanticSnapshot, item_id: OpaqueId, attribute_id: OpaqueId) -> tuple[bool, ...]: return _attribute_values(snapshot, ATTRIBUTE_BOOLEAN, item_id, attribute_id)
def reference_attribute_values(snapshot: SemanticSnapshot, item_id: OpaqueId, attribute_id: OpaqueId) -> tuple[OpaqueId, ...]: return _attribute_values(snapshot, ATTRIBUTE_REFERENCE, item_id, attribute_id)
