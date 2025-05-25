from pydantic import BaseModel, ValidationError
from electric_text.clients.functions.create_parse_result import (
    create_parse_result,
)


class FakeModel(BaseModel):
    name: str
    value: int


def test_create_parse_result_valid():
    """Test create_parse_result with valid JSON and model."""
    content = '{"name": "test", "value": 123}'
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    assert parsed_content == {"name": "test", "value": 123}
    assert isinstance(model, FakeModel)
    assert model.name == "test"
    assert model.value == 123
    assert validation_error is None
    assert json_error is None


def test_create_parse_result_validation_error():
    """Test create_parse_result with valid JSON but model validation error."""
    content = '{"name": "test", "value": "not_an_int"}'
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    assert parsed_content == {"name": "test", "value": "not_an_int"}
    assert model is None
    assert isinstance(validation_error, ValidationError)
    assert json_error is None


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
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    # parse_partial_response recovers what it can, assigning None to incomplete values
    assert parsed_content == {"name": "test", "value": None}
    assert model is None

    # Validation fails because 'value' is None, not int
    assert isinstance(validation_error, ValidationError)

    # json_error is None because parse_partial_response handles JSON decoding errors internally
    # by extracting whatever valid parts it can find rather than raising an exception
    assert json_error is None


def test_create_parse_result_partial_json():
    """Test create_parse_result with JSON embedded in text."""
    content = 'Thinking... {"name": "partial", "value": 456} trailing text'
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    assert parsed_content == {}
    assert model is None
    assert isinstance(validation_error, ValidationError)
    assert json_error is None


def test_create_parse_result_partial_json_invalid_model():
    """Test create_parse_result with embedded JSON and model validation error."""
    content = 'Thinking... {"name": "partial", "value": "wrong_type"} trailing text'
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    assert parsed_content == {}
    assert model is None
    assert isinstance(validation_error, ValidationError)
    assert json_error is None


def test_create_parse_result_no_json_found():
    """Test create_parse_result when no JSON is found in the content."""
    content = "Just some text without any JSON."
    parsed_content, model, validation_error, json_error = create_parse_result(
        content, FakeModel
    )

    assert parsed_content == {}
    assert model is None
    assert isinstance(validation_error, ValidationError)
    assert json_error is None
