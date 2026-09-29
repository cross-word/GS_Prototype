"""Non-authoritative deterministic Standard World Model diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from worldkernel import OpaqueId, SemanticSnapshot, SupportPolarity

from .vocabulary import SUBTYPE_OF


class DiagnosticSeverity(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    severity: DiagnosticSeverity
    message: str
    related_ids: tuple[OpaqueId, ...]
    support_ids: tuple[OpaqueId, ...]


def diagnose_world_model(snapshot: SemanticSnapshot) -> tuple[Diagnostic, ...]:
    edges = [support for support in snapshot.active_supports if support.polarity is SupportPolarity.POSITIVE and support.proposition.relation == SUBTYPE_OF]
    adjacency: dict[OpaqueId, set[OpaqueId]] = {}
    for support in edges:
        adjacency.setdefault(support.proposition.arguments[0], set()).add(support.proposition.arguments[1])
    components = {frozenset(node for node in adjacency if _reachable(adjacency, start, node) and _reachable(adjacency, node, start)) for start in adjacency}
    cycles = sorted((component for component in components if len(component) > 1 or any(node in adjacency.get(node, set()) for node in component)), key=lambda component: tuple(item.value for item in sorted(component, key=lambda item: item.value)))
    diagnostics = []
    for component in cycles:
        ids = tuple(sorted(component, key=lambda item: item.value))
        support_ids = tuple(sorted((support.support_id for support in edges if support.proposition.arguments[0] in component and support.proposition.arguments[1] in component), key=lambda item: item.value))
        diagnostics.append(Diagnostic("subtype_cycle", DiagnosticSeverity.WARNING, "Subtype hierarchy contains a cycle.", ids, support_ids))
    return tuple(diagnostics)


def _reachable(adjacency: dict[OpaqueId, set[OpaqueId]], start: OpaqueId, target: OpaqueId) -> bool:
    pending, seen = list(adjacency.get(start, ())), set()
    while pending:
        node = pending.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        pending.extend(adjacency.get(node, ()))
    return False
