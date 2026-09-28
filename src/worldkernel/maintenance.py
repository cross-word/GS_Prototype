"""P0.5 support-path retraction for truth maintenance."""

from __future__ import annotations

from collections.abc import Iterable

from .errors import InvalidSupportError
from .model import OpaqueId
from .support import DefaultSupport, DerivedSupport, DirectSupport, Support


def retract_support(
    supports: Iterable[Support], support_id: OpaqueId
) -> tuple[Support, ...]:
    """Retract one support and every derived support whose path becomes invalid."""

    if not isinstance(support_id, OpaqueId):
        raise InvalidSupportError(
            code="support.invalid_retraction_id",
            message="Support retraction requires an opaque support ID.",
            details={"actual_type": type(support_id).__name__},
        )
    known = _index_supports(supports)
    if support_id not in known:
        raise InvalidSupportError(
            code="support.unknown_retraction_id",
            message="Support retraction requires an active support ID.",
            details={"support_id": support_id.value},
        )

    removed = {support_id}
    changed = True
    while changed:
        changed = False
        for candidate in known.values():
            if not isinstance(candidate, (DerivedSupport, DefaultSupport)):
                continue
            if candidate.support_id in removed:
                continue
            if any(premise_id in removed for premise_id in candidate.premise_support_ids):
                removed.add(candidate.support_id)
                changed = True

    return tuple(
        known[key]
        for key in sorted(known, key=lambda item: item.value)
        if key not in removed
    )


def _index_supports(supports: Iterable[Support]) -> dict[OpaqueId, Support]:
    try:
        entries = tuple(supports)
    except TypeError as error:
        raise InvalidSupportError(
            code="support.invalid_entries",
            message="Support retraction requires iterable support entries.",
            details={"actual_type": type(supports).__name__},
        ) from error
    known: dict[OpaqueId, Support] = {}
    for support in entries:
        if not isinstance(support, (DirectSupport, DerivedSupport, DefaultSupport)):
            raise InvalidSupportError(
                code="support.invalid_entry",
                message="Support retraction accepts only recognized support entries.",
                details={"actual_type": type(support).__name__},
            )
        if support.support_id in known:
            raise InvalidSupportError(
                code="support.duplicate_id",
                message="Support IDs must be unique for retraction.",
                details={"support_id": support.support_id.value},
            )
        known[support.support_id] = support
    return known
