"""Atomic P1 vocabulary edits expressed solely as WorldPatch values."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from worldkernel import AddDirectSupport, BooleanValue, NumberValue, OpaqueId, StringValue, SupportPolarity, WorldPatch, canonical_proposition

from .vocabulary import ATTRIBUTE_BOOLEAN, ATTRIBUTE_DEF, ATTRIBUTE_NUMBER, ATTRIBUTE_REFERENCE, ATTRIBUTE_STRING, CONCEPT, ENTITY, INSTANCE_OF, LABEL, RELATED, RELATION_DEF, SUBTYPE_OF


def define_concept(patch_id: OpaqueId, concept_id: OpaqueId, *, labels: Iterable[str] = (), parent_concepts: Iterable[OpaqueId] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((CONCEPT.apply(concept_id), "concept"), *tuple((LABEL.apply(concept_id, StringValue(label)), "label") for label in sorted(labels)), *tuple((SUBTYPE_OF.apply(concept_id, parent), "subtype") for parent in sorted(parent_concepts, key=lambda item: item.value))))


def create_entity(patch_id: OpaqueId, entity_id: OpaqueId, *, labels: Iterable[str] = (), concepts: Iterable[OpaqueId] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ENTITY.apply(entity_id), "entity"), *tuple((LABEL.apply(entity_id, StringValue(label)), "label") for label in sorted(labels)), *tuple((INSTANCE_OF.apply(entity_id, concept), "instance") for concept in sorted(concepts, key=lambda item: item.value))))


def define_attribute(patch_id: OpaqueId, attribute_id: OpaqueId, *, labels: Iterable[str] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ATTRIBUTE_DEF.apply(attribute_id), "attribute"), *tuple((LABEL.apply(attribute_id, StringValue(label)), "label") for label in sorted(labels))))


def add_number_attribute(patch_id: OpaqueId, item_id: OpaqueId, attribute_id: OpaqueId, value: int | float, *, source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ATTRIBUTE_NUMBER.apply(item_id, attribute_id, NumberValue(value)), "attribute-number"),))


def add_string_attribute(patch_id: OpaqueId, item_id: OpaqueId, attribute_id: OpaqueId, value: str, *, source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ATTRIBUTE_STRING.apply(item_id, attribute_id, StringValue(value)), "attribute-string"),))


def add_boolean_attribute(patch_id: OpaqueId, item_id: OpaqueId, attribute_id: OpaqueId, value: bool, *, source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ATTRIBUTE_BOOLEAN.apply(item_id, attribute_id, BooleanValue(value)), "attribute-boolean"),))


def add_reference_attribute(patch_id: OpaqueId, item_id: OpaqueId, attribute_id: OpaqueId, value: OpaqueId, *, source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ATTRIBUTE_REFERENCE.apply(item_id, attribute_id, value), "attribute-reference"),))


def define_relation(patch_id: OpaqueId, relation_id: OpaqueId, *, labels: Iterable[str] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((RELATION_DEF.apply(relation_id), "relation"), *tuple((LABEL.apply(relation_id, StringValue(label)), "label") for label in sorted(labels))))


def add_related(patch_id: OpaqueId, relation_id: OpaqueId, subject_id: OpaqueId, object_id: OpaqueId, *, source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((RELATED.apply(relation_id, subject_id, object_id), "related"),))


def _patch(patch_id: OpaqueId, source: str, entries: tuple[tuple[object, str], ...]) -> WorldPatch:
    operations = tuple(
        AddDirectSupport(_occurrence_id(patch_id, index, proposition), proposition, SupportPolarity.POSITIVE, source)
        for index, (proposition, _) in enumerate(entries)
    )
    return WorldPatch(patch_id, operations, source)


def _occurrence_id(patch_id: OpaqueId, index: int, proposition: object) -> OpaqueId:
    payload = repr((patch_id.value, index, canonical_proposition(proposition))).encode()
    return OpaqueId(f"swm-{hashlib.sha256(payload).hexdigest()}")
