"""P0.7 immutable revisions and atomic direct-support WorldPatch commits."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from typing import Any
from .errors import PatchValidationError
from .canonical import canonical_proposition
from .model import OpaqueId
from .support import DirectSupport, TriggerProvenance

@dataclass(frozen=True, slots=True)
class AddDirectSupport:
    support_id: OpaqueId
    proposition: Any
    polarity: Any
    origin: Any
    trigger_provenance: TriggerProvenance | None = None
@dataclass(frozen=True, slots=True)
class RemoveDirectSupport:
    support_id: OpaqueId
PatchOperation = AddDirectSupport | RemoveDirectSupport
@dataclass(frozen=True, slots=True)
class WorldPatch:
    patch_id: OpaqueId
    operations: tuple[PatchOperation, ...]
    source: str
    def __post_init__(self) -> None:
        if not isinstance(self.patch_id, OpaqueId) or not isinstance(self.source, str) or not self.source:
            raise PatchValidationError("patch.invalid_metadata", "A patch requires an opaque ID and non-empty source.")
        operations = tuple(self.operations)
        if not operations:
            raise PatchValidationError("patch.empty", "A patch must contain at least one operation.")
        object.__setattr__(self, "operations", operations)
@dataclass(frozen=True, slots=True)
class CommitRecord:
    patch_id: OpaqueId
    source: str
    operations: tuple[PatchOperation, ...]
@dataclass(frozen=True, slots=True)
class Revision:
    revision_id: OpaqueId
    parent_revision_id: OpaqueId | None
    commit_record: CommitRecord | None
    supports: tuple[DirectSupport, ...]
@dataclass(frozen=True, slots=True)
class World:
    revisions: tuple[Revision, ...]
    @classmethod
    def empty(cls, world_id: OpaqueId) -> World:
        if not isinstance(world_id, OpaqueId):
            raise PatchValidationError("world.invalid_id", "A world requires an opaque ID.")
        return cls((Revision(OpaqueId(f"revision-{world_id.value}-0"), None, None, ()),))
    @property
    def current(self) -> Revision:
        return self.revisions[-1]
    def dry_run(self, patch: WorldPatch) -> tuple[DirectSupport, ...]:
        historical_ids = {support.support_id for revision in self.revisions for support in revision.supports}
        return _apply(self.current.supports, patch, historical_ids)
    def commit(self, patch: WorldPatch) -> World:
        supports = self.dry_run(patch)
        record = CommitRecord(patch.patch_id, patch.source, patch.operations)
        revision = Revision(_revision_id(self.current.revision_id, record, supports), self.current.revision_id, record, supports)
        return World((*self.revisions, revision))
def _apply(current: tuple[DirectSupport, ...], patch: WorldPatch, historical_ids: set[OpaqueId] | None = None) -> tuple[DirectSupport, ...]:
    if not isinstance(patch, WorldPatch):
        raise PatchValidationError("patch.invalid", "Commit requires a WorldPatch.")
    staged = {item.support_id: item for item in current}
    for index, operation in enumerate(patch.operations):
        try:
            if isinstance(operation, AddDirectSupport):
                if operation.support_id in staged:
                    raise PatchValidationError("patch.duplicate_support_id", "Support ID already exists.")
                if historical_ids is not None and operation.support_id in historical_ids:
                    raise PatchValidationError("patch.reused_support_id", "Support IDs cannot be reused in one world history.")
                support = DirectSupport(operation.support_id, operation.proposition, operation.polarity, operation.origin, operation.trigger_provenance)
                staged[support.support_id] = support
            elif isinstance(operation, RemoveDirectSupport):
                if not isinstance(operation.support_id, OpaqueId) or operation.support_id not in staged:
                    raise PatchValidationError("patch.missing_direct_support", "Remove requires an existing direct support ID.")
                del staged[operation.support_id]
            else:
                raise PatchValidationError("patch.invalid_operation", "Patch operation is not recognized.")
        except PatchValidationError as error:
            raise PatchValidationError(error.code, str(error), {**error.details, "operation_index": index}) from error
        except Exception as error:
            raise PatchValidationError("patch.invalid_operation", "Patch operation is structurally invalid.", {"operation_index": index}) from error
    return tuple(staged[key] for key in sorted(staged, key=lambda item: item.value))
def _revision_id(parent: OpaqueId, record: CommitRecord, supports: tuple[DirectSupport, ...]) -> OpaqueId:
    payload = repr((parent.value, record.patch_id.value, record.source, tuple(_canonical_operation(item) for item in record.operations), tuple((item.support_id.value, canonical_proposition(item.proposition), item.polarity.name, item.origin, _trigger_key(item.trigger_provenance)) for item in supports)))
    return OpaqueId(f"revision-{hashlib.sha256(payload.encode()).hexdigest()}")


def _canonical_operation(operation: PatchOperation) -> tuple[object, ...]:
    if isinstance(operation, AddDirectSupport):
        provenance = _trigger_key(operation.trigger_provenance)
        return ("add", operation.support_id.value, canonical_proposition(operation.proposition), operation.polarity.name, operation.origin, provenance)
    return ("remove", operation.support_id.value)


def _trigger_key(provenance: TriggerProvenance | None) -> tuple[str, tuple[str, ...]] | None:
    return None if provenance is None else (provenance.trigger_rule_id.value, tuple(item.value for item in provenance.premise_support_ids))
