"""P0.2 direct supports and four-state effective status evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

from .errors import InvalidSupportError
from .model import OpaqueId, Proposition


class SupportPolarity(Enum):
    """The independent positive or negative polarity of a support."""

    POSITIVE = auto()
    NEGATIVE = auto()


class SupportKind(Enum):
    """The provenance category of a support."""

    DIRECT = auto()
    DERIVED = auto()
    DEFAULT_DERIVED = auto()


@dataclass(frozen=True, slots=True)
class TriggerProvenance:
    """Historical causal metadata for one persistent trigger mutation."""

    trigger_rule_id: OpaqueId
    premise_support_ids: tuple[OpaqueId, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.trigger_rule_id, OpaqueId):
            raise InvalidSupportError("support.invalid_trigger_rule_id", "Trigger provenance requires an opaque rule ID.")
        premise_ids = tuple(self.premise_support_ids)
        if not premise_ids or not all(isinstance(item, OpaqueId) for item in premise_ids):
            raise InvalidSupportError("support.invalid_trigger_premises", "Trigger provenance requires premise support IDs.")
        object.__setattr__(self, "premise_support_ids", tuple(sorted(premise_ids, key=lambda item: item.value)))


class EffectiveStatus(Enum):
    """The open-world status computed from currently supplied supports."""

    UNKNOWN = auto()
    TRUE_ONLY = auto()
    FALSE_ONLY = auto()
    CONFLICT = auto()


@dataclass(frozen=True, slots=True)
class DirectSupport:
    """A direct reason for or against one proposition with its origin label."""

    support_id: OpaqueId
    proposition: Proposition
    polarity: SupportPolarity
    origin: str
    trigger_provenance: TriggerProvenance | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.support_id, OpaqueId):
            raise InvalidSupportError(
                code="support.invalid_id",
                message="A direct support must have an opaque support ID.",
                details={"actual_type": type(self.support_id).__name__},
            )
        if not isinstance(self.proposition, Proposition):
            raise InvalidSupportError(
                code="support.invalid_proposition",
                message="A direct support must target a well-formed proposition.",
                details={"actual_type": type(self.proposition).__name__},
            )
        if not isinstance(self.polarity, SupportPolarity):
            raise InvalidSupportError(
                code="support.invalid_polarity",
                message="A direct support must use a recognized polarity.",
                details={"actual_type": type(self.polarity).__name__},
            )
        if not isinstance(self.origin, str) or not self.origin:
            raise InvalidSupportError(
                code="support.invalid_origin",
                message="A direct support must record a non-empty origin label.",
                details={"origin": self.origin},
            )
        if self.trigger_provenance is not None and not isinstance(self.trigger_provenance, TriggerProvenance):
            raise InvalidSupportError("support.invalid_trigger_provenance", "Direct trigger provenance must be structured metadata.")

    @property
    def kind(self) -> SupportKind:
        return SupportKind.DIRECT


@dataclass(frozen=True, slots=True)
class DerivedSupport:
    """A support produced by one DERIVE rule and its premise supports."""

    support_id: OpaqueId
    proposition: Proposition
    polarity: SupportPolarity
    rule_id: OpaqueId
    premise_support_ids: tuple[OpaqueId, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.support_id, OpaqueId):
            raise InvalidSupportError(
                code="support.invalid_id",
                message="A derived support must have an opaque support ID.",
                details={"actual_type": type(self.support_id).__name__},
            )
        if not isinstance(self.proposition, Proposition):
            raise InvalidSupportError(
                code="support.invalid_proposition",
                message="A derived support must target a well-formed proposition.",
                details={"actual_type": type(self.proposition).__name__},
            )
        if not isinstance(self.polarity, SupportPolarity):
            raise InvalidSupportError(
                code="support.invalid_polarity",
                message="A derived support must use a recognized polarity.",
                details={"actual_type": type(self.polarity).__name__},
            )
        if not isinstance(self.rule_id, OpaqueId):
            raise InvalidSupportError(
                code="support.invalid_rule_id",
                message="A derived support must record an opaque rule ID.",
                details={"actual_type": type(self.rule_id).__name__},
            )
        try:
            premise_ids = tuple(self.premise_support_ids)
        except TypeError as error:
            raise InvalidSupportError(
                code="support.invalid_premise_ids",
                message="Derived premise support IDs must be iterable.",
                details={"actual_type": type(self.premise_support_ids).__name__},
            ) from error
        if not premise_ids or not all(isinstance(item, OpaqueId) for item in premise_ids):
            raise InvalidSupportError(
                code="support.invalid_premise_ids",
                message="A derived support must record one or more opaque premise IDs.",
                details={},
            )
        object.__setattr__(self, "premise_support_ids", premise_ids)

    @property
    def kind(self) -> SupportKind:
        return SupportKind.DERIVED


@dataclass(frozen=True, slots=True)
class DefaultSupport:
    """A defeasible support produced by one DEFAULT rule and its premises."""

    support_id: OpaqueId
    proposition: Proposition
    polarity: SupportPolarity
    rule_id: OpaqueId
    premise_support_ids: tuple[OpaqueId, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.support_id, OpaqueId):
            raise InvalidSupportError("support.invalid_id", "A default support must have an opaque support ID.")
        if not isinstance(self.proposition, Proposition):
            raise InvalidSupportError("support.invalid_proposition", "A default support must target a well-formed proposition.")
        if not isinstance(self.polarity, SupportPolarity):
            raise InvalidSupportError("support.invalid_polarity", "A default support must use a recognized polarity.")
        if not isinstance(self.rule_id, OpaqueId):
            raise InvalidSupportError("support.invalid_rule_id", "A default support must record an opaque rule ID.")
        try:
            premise_ids = tuple(self.premise_support_ids)
        except TypeError as error:
            raise InvalidSupportError("support.invalid_premise_ids", "Default premise support IDs must be iterable.") from error
        if not premise_ids or not all(isinstance(item, OpaqueId) for item in premise_ids):
            raise InvalidSupportError("support.invalid_premise_ids", "A default support must record one or more opaque premise IDs.")
        object.__setattr__(self, "premise_support_ids", premise_ids)

    @property
    def kind(self) -> SupportKind:
        return SupportKind.DEFAULT_DERIVED


Support: TypeAlias = DirectSupport | DerivedSupport | DefaultSupport


def default_is_defeated(support: DefaultSupport, supports: Iterable[Support]) -> bool:
    """Return whether contrary ordinary support defeats this default support."""

    if not isinstance(support, DefaultSupport):
        raise InvalidSupportError("support.invalid_default", "Default defeat requires a DefaultSupport.")
    opposite = SupportPolarity.NEGATIVE if support.polarity is SupportPolarity.POSITIVE else SupportPolarity.POSITIVE
    for candidate in supports:
        if not isinstance(candidate, (DirectSupport, DerivedSupport, DefaultSupport)):
            raise InvalidSupportError("support.invalid_entry", "Default defeat accepts only recognized supports.")
        if isinstance(candidate, (DirectSupport, DerivedSupport)) and candidate.proposition == support.proposition and candidate.polarity is opposite:
            return True
    return False


def effective_status(
    proposition: Proposition,
    supports: Iterable[Support],
) -> EffectiveStatus:
    """Compute a proposition's status without treating absence as negation."""

    if not isinstance(proposition, Proposition):
        raise InvalidSupportError(
            code="support.invalid_query_proposition",
            message="Effective status can be queried only for a well-formed proposition.",
            details={"actual_type": type(proposition).__name__},
        )

    positive = False
    negative = False
    try:
        support_entries = tuple(supports)
    except TypeError as error:
        raise InvalidSupportError(
            code="support.invalid_entries",
            message="Supports must be an iterable of support values.",
            details={"actual_type": type(supports).__name__},
        ) from error

    for support in support_entries:
        if not isinstance(support, (DirectSupport, DerivedSupport, DefaultSupport)):
            raise InvalidSupportError(
                code="support.invalid_entry",
                message="Effective status accepts only recognized support entries.",
                details={"actual_type": type(support).__name__},
            )
        if support.proposition != proposition:
            continue
        if isinstance(support, DefaultSupport) and default_is_defeated(
            support, support_entries
        ):
            continue
        if support.polarity is SupportPolarity.POSITIVE:
            positive = True
        else:
            negative = True

    if positive and negative:
        return EffectiveStatus.CONFLICT
    if positive:
        return EffectiveStatus.TRUE_ONLY
    if negative:
        return EffectiveStatus.FALSE_ONLY
    return EffectiveStatus.UNKNOWN
