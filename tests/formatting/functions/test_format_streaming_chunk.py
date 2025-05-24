import pytest
from unittest.mock import MagicMock
from typing import Optional, List
from pydantic import BaseModel

from electric_text.formatting.functions.format_streaming_chunk import (
    format_streaming_chunk,
)
from electric_text.clients.data.client_response import ClientResponse


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_format_streaming_chunk_without_model():
    """Formats streaming chunk when no model class is provided."""
    # Create mock chunk
    mock_chunk = MagicMock(spec=ClientResponse)
    mock_chunk.raw_content = "Chunk content"
    mock_chunk.is_valid = False
    mock_chunk.parsed_model = None

    # Execute function
    result = format_streaming_chunk(
        chunk=mock_chunk, 
        model_class=None
    )

    # Verify result
    assert result == "Raw chunk content: Chunk content"


def test_format_streaming_chunk_with_invalid_model():
    """Formats streaming chunk when model class provided but chunk is invalid."""
    # Create mock chunk
    mock_chunk = MagicMock(spec=ClientResponse)
    mock_chunk.raw_content = "Invalid chunk"
    mock_chunk.is_valid = False
    mock_chunk.parsed_model = None

    # Execute function
    result = format_streaming_chunk(
        chunk=mock_chunk, 
        model_class=SampleResponseModel
    )

    # Verify result
    assert result == "Raw chunk content: Invalid chunk"


def test_format_streaming_chunk_with_valid_model():
    """Formats streaming chunk when model class provided and chunk is valid."""
    # Create model instance
    model_instance = SampleResponseModel(content="chunk1", items=["x", "y"])

    # Create mock chunk
    mock_chunk = MagicMock(spec=ClientResponse)
    mock_chunk.raw_content = '{"content": "chunk1", "items": ["x", "y"]}'
    mock_chunk.is_valid = True
    mock_chunk.parsed_model = model_instance

    # Execute function
    result = format_streaming_chunk(
        chunk=mock_chunk, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert "Valid chunk:" in result
    assert '"content": "chunk1"' in result
    assert '"items":' in result
    assert '"x"' in result
    assert '"y"' in result


def test_format_streaming_chunk_with_valid_model_no_parsed_model():
    """Formats streaming chunk when model class provided, is_valid=True but no parsed_model."""
    # Create mock chunk
    mock_chunk = MagicMock(spec=ClientResponse)
    mock_chunk.raw_content = "Some chunk content"
    mock_chunk.is_valid = True
    mock_chunk.parsed_model = None

    # Execute function
    result = format_streaming_chunk(
        chunk=mock_chunk, 
        model_class=SampleResponseModel
    )

    # Verify result
    assert result == "Raw chunk content: Some chunk content" 