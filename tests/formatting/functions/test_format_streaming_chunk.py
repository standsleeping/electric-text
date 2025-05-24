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


def test_format_streaming_chunk_without_model():
    """Formats streaming chunk when no model class is provided."""
    result = format_streaming_chunk(
        content="Test response content",
        model_class=None
    )

    # Should use content formatting since content is available
    assert result == "PARTIAL RESULT (UNSTRUCTURED):\nTest response content"


def test_format_streaming_chunk_with_invalid_model():
    """Formats streaming chunk when model class provided but chunk is invalid."""
    result = format_streaming_chunk(
        content="",
        is_valid=False,
        parsed_model=None,
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no content
    assert result == "PARTIAL RESULT (UNSTRUCTURED): [No content available]"


def test_format_streaming_chunk_with_valid_model():
    """Formats streaming chunk when model class provided and chunk is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="chunk1", items=["x", "y"])

    result = format_streaming_chunk(
        content="",
        is_valid=True,
        parsed_model=model_instance,
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
    result = format_streaming_chunk(
        content="",
        is_valid=True,
        parsed_model=None,
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no parsed_model or content
    assert result == "PARTIAL RESULT (UNSTRUCTURED): [No content available]"


def test_format_streaming_chunk_with_tool_call_content():
    """Formats streaming chunk with tool call content."""
    content = (
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    
    result = format_streaming_chunk(
        content=content,
        model_class=None
    )

    expected = (
        "PARTIAL RESULT (UNSTRUCTURED):\n"
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    assert result == expected