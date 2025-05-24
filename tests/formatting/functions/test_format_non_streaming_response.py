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


def test_format_non_streaming_response_without_model():
    """Formats non-streaming response when no model class is provided."""
    result = format_non_streaming_response(
        content="Test response content",
        model_class=None
    )

    # Should use content formatting since content is available
    assert result == "RESULT (UNSTRUCTURED):\nTest response content"


def test_format_non_streaming_response_with_invalid_model():
    """Formats non-streaming response when model class provided but response is invalid."""
    result = format_non_streaming_response(
        content="",
        is_valid=False,
        parsed_model=None,
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no content
    assert result == "RESULT (UNSTRUCTURED): [No content available]"


def test_format_non_streaming_response_with_valid_model():
    """Formats non-streaming response when model class provided and response is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="test", items=["a", "b"])

    result = format_non_streaming_response(
        content="",
        is_valid=True,
        parsed_model=model_instance,
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
    result = format_non_streaming_response(
        content="",
        is_valid=True,
        parsed_model=None,
        model_class=SampleResponseModel
    )

    # Should fall back to no content message since no parsed_model or content
    assert result == "RESULT (UNSTRUCTURED): [No content available]"


def test_format_non_streaming_response_with_tool_call_content():
    """Formats non-streaming response with tool call content."""
    content = (
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    
    result = format_non_streaming_response(
        content=content,
        model_class=None
    )

    expected = (
        "RESULT (UNSTRUCTURED):\n"
        "I'll check the weather for you.\n"
        'TOOL CALL: get_weather\nINPUTS: {"location": "Chicago"}'
    )
    assert result == expected