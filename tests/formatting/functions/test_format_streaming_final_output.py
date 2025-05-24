import pytest
import json
from typing import Optional, List
from pydantic import BaseModel

from electric_text.formatting.functions.format_streaming_final_output import (
    format_streaming_final_output,
)


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_format_streaming_final_output_without_model():
    """Formats streaming final output when no model class is provided."""
    full_content = '{"content": "test", "items": ["a", "b"]}'

    # Execute function
    result = format_streaming_final_output(
        full_content=full_content, 
        model_class=None
    )

    # Verify result
    expected = f"FULL RESULT: {full_content}"
    assert result == expected


def test_format_streaming_final_output_with_model_valid_json():
    """Formats streaming final output when model class provided and content is valid JSON."""
    full_content = '{"content": "test", "items": ["a", "b"]}'

    # Execute function
    result = format_streaming_final_output(
        full_content=full_content, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert f"FULL RESULT: {full_content}" in result
    assert "RESULT TO JSON:" in result
    # The JSON part should contain the parsed structure
    assert '"content": "test"' in result
    assert '"items": ["a", "b"]' in result


def test_format_streaming_final_output_with_model_invalid_json():
    """Formats streaming final output when model class provided but content is invalid JSON."""
    full_content = "Invalid JSON content"

    # Execute function
    result = format_streaming_final_output(
        full_content=full_content, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert f"FULL RESULT: {full_content}" in result
    assert "ERROR PARSING JSON:" in result
    assert f"STRUCTURED FULL RESULT: {full_content}" in result


def test_format_streaming_final_output_with_model_empty_content():
    """Formats streaming final output when model class provided but content is empty."""
    full_content = ""

    # Execute function
    result = format_streaming_final_output(
        full_content=full_content, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert "FULL RESULT: " in result
    assert "ERROR PARSING JSON:" in result
    assert "STRUCTURED FULL RESULT: " in result


def test_format_streaming_final_output_with_model_complex_json():
    """Formats streaming final output with complex nested JSON structure."""
    full_content = '{"content": "complex", "items": ["x", "y", "z"], "nested": {"key": "value"}}'

    # Execute function
    result = format_streaming_final_output(
        full_content=full_content, 
        model_class=SampleResponseModel
    )

    # Verify result contains expected parts
    assert f"FULL RESULT: {full_content}" in result
    assert "RESULT TO JSON:" in result
    assert '"content": "complex"' in result
    assert '"items": ["x", "y", "z"]' in result
    assert '"nested": {"key": "value"}' in result 