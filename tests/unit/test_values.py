import pytest

from worldkernel import (
    BooleanValue,
    InvalidScalarValueError,
    NumberValue,
    StringValue,
)


def test_scalar_values_are_immutable_hashable_value_objects() -> None:
    values = {
        NumberValue(10),
        NumberValue(10.0),
        BooleanValue(True),
        StringValue("ten"),
    }

    assert len(values) == 3
    assert NumberValue(10) == NumberValue(10.0)


@pytest.mark.parametrize("value", [True, "10", None, float("nan"), float("inf")])
def test_number_rejects_non_numeric_or_non_finite_values(value: object) -> None:
    with pytest.raises(InvalidScalarValueError) as error:
        NumberValue(value)  # type: ignore[arg-type]

    assert error.value.code == "value.invalid_number"


@pytest.mark.parametrize("value", [1, "true", None])
def test_boolean_rejects_non_boolean_values(value: object) -> None:
    with pytest.raises(InvalidScalarValueError) as error:
        BooleanValue(value)  # type: ignore[arg-type]

    assert error.value.code == "value.invalid_boolean"


@pytest.mark.parametrize("value", [1, True, None])
def test_string_rejects_non_string_values(value: object) -> None:
    with pytest.raises(InvalidScalarValueError) as error:
        StringValue(value)  # type: ignore[arg-type]

    assert error.value.code == "value.invalid_string"

