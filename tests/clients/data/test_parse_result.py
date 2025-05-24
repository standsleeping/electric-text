import json
import pytest
from pydantic import BaseModel, ValidationError
from electric_text.clients import ParseResult


# Example model for response validation
class ExampleModel(BaseModel):
    name: str
    value: int


def test_parse_result_valid():
    """Test ParseResult with valid model instance."""
    parsed_content = {"name": "test", "value": 42}
    model = ExampleModel(name="test", value=42)

    result = ParseResult(
        parsed_content=parsed_content,
        model=model,
    )

    assert result.parsed_content == parsed_content
    assert result.model == model
    assert result.validation_error is None
    assert result.json_error is None
    assert result.is_valid is True


def test_parse_result_validation_error():
    """Test ParseResult with validation error."""
    parsed_content = {"name": "test", "value": "not_an_int"}

    # Create a validation error
    try:
        ExampleModel(**parsed_content)
        pytest.fail("Should have raised ValidationError")
    except ValidationError as e:
        validation_error = e

    result = ParseResult(
        parsed_content=parsed_content,
        validation_error=validation_error,
    )

    assert result.parsed_content == parsed_content
    assert result.model is None
    assert result.validation_error is validation_error
    assert result.json_error is None
    assert result.is_valid is False


def test_parse_result_json_error():
    """Test ParseResult with JSON error."""
    parsed_content = {}

    # Create a JSON error
    raw_content = '{"name": "test", "value": 42'  # Incomplete JSON
    try:
        json.loads(raw_content)
        pytest.fail("Should have raised JSONDecodeError")
    except json.JSONDecodeError as e:
        json_error = e

    result = ParseResult(
        parsed_content=parsed_content,
        json_error=json_error,
    )

    assert result.parsed_content == parsed_content
    assert result.model is None
    assert result.validation_error is None
    assert result.json_error is json_error
    assert result.is_valid is False


def test_is_valid_property():
    """Test the is_valid property."""
    # Valid case
    valid_result = ParseResult(
        parsed_content={}, model=ExampleModel(name="test", value=42)
    )
    assert valid_result.is_valid is True

    # Invalid cases
    invalid_result1 = ParseResult(parsed_content={}, model=None)
    assert invalid_result1.is_valid is False

    # Create a validation error directly
    try:
        ExampleModel(name="test", value="not an integer")
        pytest.fail("Should have raised ValidationError")
    except ValidationError as e:
        validation_error = e

    invalid_result2 = ParseResult(
        parsed_content={},
        validation_error=validation_error,
    )

    assert invalid_result2.is_valid is False
