"""P0.10 frozen evaluated semantic snapshots and orchestration."""
from __future__ import annotations
from dataclasses import dataclass
from .defaults import DefaultRule, evaluate_defaults
from .rules import DeriveRule, derive_closure
from .support import DefaultSupport, DirectSupport, Support, default_is_defeated, effective_status
from .model import OpaqueId, Proposition
from .world import World

@dataclass(frozen=True, slots=True)
class SemanticSnapshot:
    revision_id: OpaqueId
    direct_supports: tuple[DirectSupport, ...]
    derived_supports: tuple[Support, ...]
    default_supports: tuple[DefaultSupport, ...]
    def __post_init__(self) -> None:
        object.__setattr__(self, "direct_supports", tuple(self.direct_supports))
        object.__setattr__(self, "derived_supports", tuple(self.derived_supports))
        object.__setattr__(self, "default_supports", tuple(self.default_supports))
    @property
    def supports(self) -> tuple[Support, ...]:
        return (*self.direct_supports, *self.derived_supports, *self.default_supports)
    @property
    def active_supports(self) -> tuple[Support, ...]:
        return tuple(item for item in self.supports if not isinstance(item, DefaultSupport) or not default_is_defeated(item, self.supports))
    def supports_for(self, proposition: Proposition) -> tuple[Support, ...]:
        return tuple(item for item in self.supports if item.proposition == proposition)
    def effective_status(self, proposition: Proposition):
        return effective_status(proposition, self.supports)

@dataclass(frozen=True, slots=True)
class SemanticRuntime:
    derive_rules: tuple[DeriveRule, ...] = ()
    default_rules: tuple[DefaultRule, ...] = ()
    def evaluate(self, world: World) -> SemanticSnapshot:
        direct = tuple(world.current.supports)
        closure = derive_closure(self.derive_rules, direct)
        derived = tuple(item for item in closure if item not in direct)
        complete = evaluate_defaults(self.default_rules, closure)
        defaults = tuple(item for item in complete if isinstance(item, DefaultSupport))
        return SemanticSnapshot(world.current.revision_id, direct, derived, defaults)
