from pydantic import BaseModel, ValidationError
from electric_text.clients.data import ParseResult
from electric_text.clients.functions.create_parse_result import (
    create_parse_result,
)


class FakeModel(BaseModel):
    name: str
    value: int


def test_create_parse_result_valid():
    """Test create_parse_result with valid JSON and model."""
    content = '{"name": "test", "value": 123}'
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)
    assert result.parsed_content == {"name": "test", "value": 123}
    assert isinstance(result.model, FakeModel)
    assert result.model.name == "test"
    assert result.model.value == 123
    assert result.validation_error is None
    assert result.json_error is None
    assert result.is_valid is True


def test_create_parse_result_validation_error():
    """Test create_parse_result with valid JSON but model validation error."""
    content = '{"name": "test", "value": "not_an_int"}'
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)
    assert result.parsed_content == {"name": "test", "value": "not_an_int"}
    assert result.model is None
    assert isinstance(result.validation_error, ValidationError)
    assert result.json_error is None
    assert result.is_valid is False


def test_create_parse_result_json_error():
    """Test create_parse_result with invalid/incomplete JSON.

    Note: Although the input is invalid JSON, parse_partial_response is designed
    to recover as much information as possible from partial JSON. It handles the
    JSONDecodeError internally and attempts to extract valid key-value pairs.

    In this test, we're verifying that:
    1. Partial values are extracted and set to None when they can't be fully parsed
    2. Validation fails because the extracted content doesn't match the model
    3. json_error is None because parse_partial_response handles the JSON error internally
    """
    content = '{"name": "test", "value": 123'  # Incomplete JSON (missing closing brace)
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)

    # parse_partial_response recovers what it can, assigning None to incomplete values
    assert result.parsed_content == {"name": "test", "value": None}
    assert result.model is None

    # Validation fails because 'value' is None, not int
    assert isinstance(result.validation_error, ValidationError)

    # json_error is None because parse_partial_response handles JSON decoding errors internally
    # by extracting whatever valid parts it can find rather than raising an exception
    assert result.json_error is None
    assert result.is_valid is False


def test_create_parse_result_partial_json():
    """Test create_parse_result with JSON embedded in text."""
    content = 'Thinking... {"name": "partial", "value": 456} trailing text'
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)
    assert result.parsed_content == {}
    assert result.model is None
    assert isinstance(result.validation_error, ValidationError)
    assert result.json_error is None
    assert result.is_valid is False


def test_create_parse_result_partial_json_invalid_model():
    """Test create_parse_result with embedded JSON and model validation error."""
    content = 'Thinking... {"name": "partial", "value": "wrong_type"} trailing text'
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)
    assert result.parsed_content == {}
    assert result.model is None
    assert isinstance(result.validation_error, ValidationError)
    assert result.json_error is None
    assert result.is_valid is False


def test_create_parse_result_no_json_found():
    """Test create_parse_result when no JSON is found in the content."""
    content = "Just some text without any JSON."
    result = create_parse_result(content, FakeModel)

    assert isinstance(result, ParseResult)
    assert result.parsed_content == {}
    assert result.model is None
    assert isinstance(result.validation_error, ValidationError)
    assert result.json_error is None
    assert result.is_valid is False
