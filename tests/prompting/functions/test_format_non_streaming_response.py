from unittest.mock import MagicMock
from typing import Optional, List
from pydantic import BaseModel

from electric_text.prompting.functions.format_non_streaming_response import (
    format_non_streaming_response,
)
from electric_text.clients.data.client_response import ClientResponse


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_format_non_streaming_response_without_model():
    """Formats non-streaming response when no model class is provided."""
    # Create mock response
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = "Test response content"
    mock_response.is_valid = False
    mock_response.parsed_model = None

    # Execute function
    result = format_non_streaming_response(
        response=mock_response, 
        model_class=None
    )

    # Verify result
    assert result == "Raw content (no model class): Test response content"


def test_format_non_streaming_response_with_invalid_model():
    """Formats non-streaming response when model class provided but response is invalid."""
    # Create mock response
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = "Invalid JSON content"
    mock_response.is_valid = False
    mock_response.parsed_model = None

    # Execute function
    result = format_non_streaming_response(
        response=mock_response, 
        model_class=SampleResponseModel
    )

    # Verify result
    assert result == "Raw content (no model class): Invalid JSON content"


def test_format_non_streaming_response_with_valid_model():
    """Formats non-streaming response when model class provided and response is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="test", items=["a", "b"])

    # Create mock response
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = '{"content": "test", "items": ["a", "b"]}'
    mock_response.is_valid = True
    mock_response.parsed_model = model_instance

    # Execute function
    result = format_non_streaming_response(
        response=mock_response, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert "Result:" in result
    assert '"content": "test"' in result
    assert '"items":' in result
    assert '"a"' in result
    assert '"b"' in result


def test_format_non_streaming_response_with_valid_model_no_parsed_model():
    """Formats non-streaming response when model class provided, is_valid=True but no parsed_model."""
    # Create mock response
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.raw_content = "Some content"
    mock_response.is_valid = True
    mock_response.parsed_model = None

    # Execute function
    result = format_non_streaming_response(
        response=mock_response, 
        model_class=SampleResponseModel
    )

    # Verify result
    assert result == "Raw content (no model class): Some content" 