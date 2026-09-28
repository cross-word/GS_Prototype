from dataclasses import FrozenInstanceError

import pytest

from worldkernel import (
    ArgumentKind,
    DirectSupport,
    EffectiveStatus,
    InvalidSupportError,
    OpaqueId,
    RelationSchema,
    SupportPolarity,
    effective_status,
)


@pytest.fixture
def mortal_proposition():
    mortal = RelationSchema("Mortal", (ArgumentKind.ID,))
    return mortal.apply(OpaqueId("smaug"))


def test_direct_support_retains_domain_neutral_provenance(mortal_proposition) -> None:
    support = DirectSupport(
        support_id=OpaqueId("support-001"),
        proposition=mortal_proposition,
        polarity=SupportPolarity.POSITIVE,
        origin="player-input",
    )

    assert support.support_id == OpaqueId("support-001")
    assert support.proposition is mortal_proposition
    assert support.polarity is SupportPolarity.POSITIVE
    assert support.origin == "player-input"

    with pytest.raises(FrozenInstanceError):
        support.origin = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("supports", "expected_status"),
    [
        ((), EffectiveStatus.UNKNOWN),
        ((SupportPolarity.POSITIVE,), EffectiveStatus.TRUE_ONLY),
        ((SupportPolarity.NEGATIVE,), EffectiveStatus.FALSE_ONLY),
        (
            (SupportPolarity.POSITIVE, SupportPolarity.NEGATIVE),
            EffectiveStatus.CONFLICT,
        ),
    ],
)
def test_effective_status_is_computed_from_independent_polarities(
    mortal_proposition,
    supports,
    expected_status,
) -> None:
    direct_supports = tuple(
        DirectSupport(
            support_id=OpaqueId(f"support-{index}"),
            proposition=mortal_proposition,
            polarity=polarity,
            origin="test",
        )
        for index, polarity in enumerate(supports)
    )

    assert effective_status(mortal_proposition, direct_supports) is expected_status


def test_effective_status_ignores_support_for_a_different_proposition(
    mortal_proposition,
) -> None:
    dragon = RelationSchema("Dragon", (ArgumentKind.ID,)).apply(OpaqueId("smaug"))
    unrelated_support = DirectSupport(
        support_id=OpaqueId("support-dragon"),
        proposition=dragon,
        polarity=SupportPolarity.POSITIVE,
        origin="test",
    )

    assert effective_status(mortal_proposition, (unrelated_support,)) is EffectiveStatus.UNKNOWN


@pytest.mark.parametrize(
    ("field", "value", "error_code"),
    [
        ("support_id", "support-001", "support.invalid_id"),
        ("proposition", "Mortal(smaug)", "support.invalid_proposition"),
        ("polarity", "positive", "support.invalid_polarity"),
        ("origin", "", "support.invalid_origin"),
    ],
)
def test_direct_support_rejects_malformed_fields(
    mortal_proposition,
    field,
    value,
    error_code,
) -> None:
    fields = {
        "support_id": OpaqueId("support-001"),
        "proposition": mortal_proposition,
        "polarity": SupportPolarity.POSITIVE,
        "origin": "test",
    }
    fields[field] = value

    with pytest.raises(InvalidSupportError) as error:
        DirectSupport(**fields)

    assert error.value.code == error_code


def test_effective_status_rejects_non_support_entries(mortal_proposition) -> None:
    with pytest.raises(InvalidSupportError) as error:
        effective_status(mortal_proposition, ("not-a-support",))

    assert error.value.code == "support.invalid_entry"
