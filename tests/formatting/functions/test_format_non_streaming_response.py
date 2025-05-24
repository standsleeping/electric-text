from typing import Optional, List
from pydantic import BaseModel

from electric_text.formatting.functions.format_non_streaming_response import (
    format_non_streaming_response,
)
from electric_text.clients.data.client_response import ClientResponse
from electric_text.clients.data.prompt_result import PromptResult
from electric_text.clients.data.parse_result import ParseResult


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_format_non_streaming_response_without_model(sample_client_response_unstructured):
    """Formats non-streaming response when no model class is provided."""
    result = format_non_streaming_response(
        response=sample_client_response_unstructured, 
        model_class=None
    )

    # Should use content blocks formatting since they're available
    assert result == "RESULT (UNSTRUCTURED):\nTest response content"


def test_format_non_streaming_response_with_invalid_model():
    """Formats non-streaming response when model class provided but response is invalid."""
    # Create response with empty content blocks to test fallback
    prompt_result = PromptResult(content_blocks=[])
    response = ClientResponse.from_prompt_result(prompt_result)

    result = format_non_streaming_response(
        response=response, 
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no content blocks
    assert result == "RESULT (UNSTRUCTURED): [No content available]"


def test_format_non_streaming_response_with_valid_model():
    """Formats non-streaming response when model class provided and response is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="test", items=["a", "b"])

    # Create valid parse result
    parse_result = ParseResult(
        parsed_content={"content": "test", "items": ["a", "b"]},
        model=model_instance,
        validation_error=None,
        json_error=None
    )
    response = ClientResponse.from_parse_result(parse_result)

    result = format_non_streaming_response(
        response=response, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert "RESULT (STRUCTURED):" in result
    assert '"content": "test"' in result
    assert '"items":' in result
    assert '"a"' in result
    assert '"b"' in result


def test_format_non_streaming_response_with_valid_model_no_parsed_model():
    """Formats non-streaming response when model class provided, is_valid=True but no parsed_model."""
    # Create parse result that's valid but no model (edge case)
    parse_result = ParseResult(
        parsed_content={},
        model=None,
        validation_error=None,
        json_error=None
    )
    response = ClientResponse.from_parse_result(parse_result)

    result = format_non_streaming_response(
        response=response, 
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no parsed_model or content blocks
    assert result == "RESULT (UNSTRUCTURED): [No content available]"


def test_format_non_streaming_response_with_tool_call_content_blocks(sample_client_response_with_tool_call):
    """Formats non-streaming response with tool call content blocks."""
    result = format_non_streaming_response(
        response=sample_client_response_with_tool_call,
        model_class=None
    )

    expected = (
        "RESULT (UNSTRUCTURED):\n"
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    assert result == expected