"""P0.9 machine-readable support justification graphs."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable
from .model import OpaqueId, Proposition
from .support import DefaultSupport, DerivedSupport, DirectSupport, Support, SupportKind

@dataclass(frozen=True, slots=True)
class JustificationNode:
    support_id: OpaqueId
    kind: SupportKind
    rule_id: OpaqueId | None
    premise_support_ids: tuple[OpaqueId, ...]
    revision_id: OpaqueId | None
@dataclass(frozen=True, slots=True)
class JustificationGraph:
    nodes: tuple[JustificationNode, ...]
    edges: tuple[tuple[OpaqueId, OpaqueId], ...]

def why(proposition: Proposition, supports: Iterable[Support], revision_id: OpaqueId | None = None) -> JustificationGraph:
    """Return every support path for a proposition as a deterministic graph."""
    entries = tuple(supports); index = {item.support_id: item for item in entries}
    roots = [item for item in entries if item.proposition == proposition]
    seen: set[OpaqueId] = set(); nodes = []; edges = []
    def visit(item: Support) -> None:
        if item.support_id in seen: return
        seen.add(item.support_id)
        if isinstance(item, DirectSupport): rule_id = None; premises = ()
        else: rule_id = item.rule_id; premises = item.premise_support_ids
        nodes.append(JustificationNode(item.support_id, item.kind, rule_id, premises, revision_id))
        for premise_id in premises:
            edges.append((item.support_id, premise_id))
            if premise_id in index: visit(index[premise_id])
    for root in sorted(roots, key=lambda item: item.support_id.value): visit(root)
    return JustificationGraph(tuple(sorted(nodes, key=lambda item: item.support_id.value)), tuple(sorted(edges, key=lambda item: (item[0].value, item[1].value))))
