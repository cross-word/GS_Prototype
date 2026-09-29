"""Atomic P1 vocabulary edits expressed solely as WorldPatch values."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from worldkernel import AddDirectSupport, OpaqueId, StringValue, SupportPolarity, WorldPatch, canonical_proposition

from .vocabulary import CONCEPT, ENTITY, LABEL


def define_concept(patch_id: OpaqueId, concept_id: OpaqueId, *, labels: Iterable[str] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((CONCEPT.apply(concept_id), "concept"), *tuple((LABEL.apply(concept_id, StringValue(label)), "label") for label in sorted(labels))))


def create_entity(patch_id: OpaqueId, entity_id: OpaqueId, *, labels: Iterable[str] = (), source: str = "worldmodel") -> WorldPatch:
    return _patch(patch_id, source, ((ENTITY.apply(entity_id), "entity"), *tuple((LABEL.apply(entity_id, StringValue(label)), "label") for label in sorted(labels))))


def _patch(patch_id: OpaqueId, source: str, entries: tuple[tuple[object, str], ...]) -> WorldPatch:
    operations = tuple(
        AddDirectSupport(_occurrence_id(patch_id, index, proposition), proposition, SupportPolarity.POSITIVE, source)
        for index, (proposition, _) in enumerate(entries)
    )
    return WorldPatch(patch_id, operations, source)


def _occurrence_id(patch_id: OpaqueId, index: int, proposition: object) -> OpaqueId:
    payload = repr((patch_id.value, index, canonical_proposition(proposition))).encode()
    return OpaqueId(f"swm-{hashlib.sha256(payload).hexdigest()}")
