"""P0.2 direct supports and four-state effective status evaluation."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto

from .errors import InvalidSupportError
from .model import OpaqueId, Proposition


class SupportPolarity(Enum):
    """The independent positive or negative polarity of a support."""

    POSITIVE = auto()
    NEGATIVE = auto()


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


def effective_status(
    proposition: Proposition,
    supports: Iterable[DirectSupport],
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
        support_entries = iter(supports)
    except TypeError as error:
        raise InvalidSupportError(
            code="support.invalid_entries",
            message="Supports must be an iterable of DirectSupport values.",
            details={"actual_type": type(supports).__name__},
        ) from error

    for support in support_entries:
        if not isinstance(support, DirectSupport):
            raise InvalidSupportError(
                code="support.invalid_entry",
                message="Effective status accepts only DirectSupport entries in P0.2.",
                details={"actual_type": type(support).__name__},
            )
        if support.proposition != proposition:
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
