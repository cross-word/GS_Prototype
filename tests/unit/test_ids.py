import pytest

from worldkernel import InvalidIdError, OpaqueId


def test_opaque_ids_have_stable_value_equality_and_hashing() -> None:
    first = OpaqueId("rabbit-512")
    same = OpaqueId("rabbit-512")
    other = OpaqueId("rabbit-513")

    assert first == same
    assert hash(first) == hash(same)
    assert first != other
    assert len({first, same, other}) == 2


def test_opaque_id_has_an_explicit_safe_string_representation() -> None:
    identifier = OpaqueId("rabbit-512")

    assert str(identifier) == "@rabbit-512"
    assert repr(identifier) == "OpaqueId('rabbit-512')"


@pytest.mark.parametrize("value", ["", 123, None])
def test_opaque_id_rejects_invalid_runtime_values(value: object) -> None:
    with pytest.raises(InvalidIdError) as error:
        OpaqueId(value)  # type: ignore[arg-type]

    assert error.value.code == "id.invalid_value"
    assert "value" in error.value.details

