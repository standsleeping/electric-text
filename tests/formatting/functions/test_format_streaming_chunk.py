from typing import Optional, List
from pydantic import BaseModel

from electric_text.formatting.functions.format_streaming_chunk import (
    format_streaming_chunk,
)
from electric_text.clients.data.client_response import ClientResponse
from electric_text.clients.data.prompt_result import PromptResult
from electric_text.clients.data.parse_result import ParseResult


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_format_streaming_chunk_without_model(sample_client_response_unstructured):
    """Formats streaming chunk when no model class is provided."""
    result = format_streaming_chunk(
        chunk=sample_client_response_unstructured, 
        model_class=None
    )

    # Should use content blocks formatting since they're available
    assert result == "PARTIAL RESULT (UNSTRUCTURED):\nTest response content"


def test_format_streaming_chunk_with_invalid_model():
    """Formats streaming chunk when model class provided but chunk is invalid."""
    # Create response with empty content blocks to test fallback
    prompt_result = PromptResult(content_blocks=[])
    chunk = ClientResponse.from_prompt_result(prompt_result)

    result = format_streaming_chunk(
        chunk=chunk, 
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no content blocks
    assert result == "PARTIAL RESULT (UNSTRUCTURED): [No content available]"


def test_format_streaming_chunk_with_valid_model():
    """Formats streaming chunk when model class provided and chunk is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="chunk1", items=["x", "y"])

    # Create valid parse result
    parse_result = ParseResult(
        parsed_content={"content": "chunk1", "items": ["x", "y"]},
        model=model_instance,
        validation_error=None,
        json_error=None
    )
    chunk = ClientResponse.from_parse_result(parse_result)

    result = format_streaming_chunk(
        chunk=chunk, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert "PARTIAL RESULT (STRUCTURED):" in result
    assert '"content": "chunk1"' in result
    assert '"items":' in result
    assert '"x"' in result
    assert '"y"' in result


def test_format_streaming_chunk_with_valid_model_no_parsed_model():
    """Formats streaming chunk when model class provided, is_valid=True but no parsed_model."""
    # Create parse result that's valid but no model (edge case)
    parse_result = ParseResult(
        parsed_content={},
        model=None,
        validation_error=None,
        json_error=None
    )
    chunk = ClientResponse.from_parse_result(parse_result)

    result = format_streaming_chunk(
        chunk=chunk, 
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no parsed_model or content blocks
    assert result == "PARTIAL RESULT (UNSTRUCTURED): [No content available]"


def test_format_streaming_chunk_with_tool_call_content_blocks(sample_client_response_with_tool_call):
    """Formats streaming chunk with tool call content blocks."""
    result = format_streaming_chunk(
        chunk=sample_client_response_with_tool_call,
        model_class=None
    )

    expected = (
        "PARTIAL RESULT (UNSTRUCTURED):\n"
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    assert result == expected