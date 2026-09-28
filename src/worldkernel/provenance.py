"""P0.9 machine-readable support justification graphs."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable, Mapping
from .model import OpaqueId, Proposition
from .world import World
from .support import (
    DefaultSupport,
    DirectSupport,
    Support,
    SupportKind,
    SupportPolarity,
    default_is_defeated,
)

@dataclass(frozen=True, slots=True)
class JustificationNode:
    support_id: OpaqueId
    proposition: Proposition
    polarity: SupportPolarity
    kind: SupportKind
    origin: str | None
    rule_id: OpaqueId | None
    premise_support_ids: tuple[OpaqueId, ...]
    originating_revision_id: OpaqueId | None
    default_is_defeated: bool | None


@dataclass(frozen=True, slots=True)
class JustificationGraph:
    nodes: tuple[JustificationNode, ...]
    edges: tuple[tuple[OpaqueId, OpaqueId], ...]
    queried_at_revision_id: OpaqueId | None

def why(proposition: Proposition, supports: Iterable[Support], revision_id: OpaqueId | None = None, originating_revisions: Mapping[OpaqueId, OpaqueId] | None = None, root_supports: Iterable[Support] | None = None) -> JustificationGraph:
    """Return every support path for a proposition as a deterministic graph."""
    entries = tuple(supports); index = {item.support_id: item for item in entries}
    roots = [item for item in (entries if root_supports is None else tuple(root_supports)) if item.proposition == proposition]
    seen: set[OpaqueId] = set(); nodes = []; edges = []
    def visit(item: Support) -> None:
        if item.support_id in seen: return
        seen.add(item.support_id)
        if isinstance(item, DirectSupport) and item.trigger_provenance is not None:
            rule_id = item.trigger_provenance.trigger_rule_id; premises = item.trigger_provenance.premise_support_ids
            for frozen in item.trigger_provenance.frozen_supports:
                index.setdefault(frozen.support_id, frozen)
        elif isinstance(item, DirectSupport): rule_id = None; premises = ()
        else: rule_id = item.rule_id; premises = item.premise_support_ids
        origin = item.origin if isinstance(item, DirectSupport) else None
        defeated = default_is_defeated(item, entries) if isinstance(item, DefaultSupport) else None
        nodes.append(
            JustificationNode(
                item.support_id,
                item.proposition,
                item.polarity,
                item.kind,
                origin,
                rule_id,
                premises,
                None if originating_revisions is None else originating_revisions.get(item.support_id),
                defeated,
            )
        )
        for premise_id in premises:
            edges.append((item.support_id, premise_id))
            if premise_id in index: visit(index[premise_id])
    for root in sorted(roots, key=lambda item: item.support_id.value): visit(root)
    return JustificationGraph(
        tuple(sorted(nodes, key=lambda item: item.support_id.value)),
        tuple(sorted(edges, key=lambda item: (item[0].value, item[1].value))),
        revision_id,
    )


def why_in_world(world: World, proposition: Proposition) -> JustificationGraph:
    """Query current support with immutable history available for causal provenance."""
    origins: dict[OpaqueId, OpaqueId] = {}
    historical: list[Support] = []
    for revision in world.revisions:
        for support in revision.supports:
            origins.setdefault(support.support_id, revision.revision_id)
            historical.append(support)
    entries = (*historical, *world.current.supports)
    return why(proposition, entries, world.current.revision_id, origins, world.current.supports)
