from dataclasses import dataclass
from typing import Dict, Any
from unittest.mock import patch

from electric_text.transformers import structured_output_transformer
from electric_text.capabilities import ProviderCapabilities


@dataclass
class MockModel:
    name: str
    value: int

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"name": {"type": "string"}, "value": {"type": "integer"}},
        }


def test_structured_output_transformer_no_model():
    """Test with no model in context."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test"}

    result = structured_output_transformer(request, context)
    assert result == request
    assert result is not request  # Should be a copy


def test_structured_output_transformer_unsupported():
    """Test with a provider that doesn't support structured output."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "unsupported", "response_model": MockModel}

    with patch.object(ProviderCapabilities, "supports", return_value=False):
        result = structured_output_transformer(request, context)
        assert result == request
        assert result is not request  # Should be a copy


def test_structured_output_transformer_fixed_value():
    """Test with a provider that uses fixed value for structured output."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test", "response_model": MockModel}

    # Mock the capability check and parameters
    with patch.object(ProviderCapabilities, "supports", return_value=True):
        with patch.object(
            ProviderCapabilities,
            "get_capability_params",
            return_value={"param": "structured_format", "value": {"type": "json"}},
        ):
            result = structured_output_transformer(request, context)
            assert result != request
            assert "structured_format" in result
            assert result["structured_format"] == {"type": "json"}


def test_structured_output_transformer_schema_method():
    """Test with a provider that uses schema method for structured output."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test", "response_model": MockModel}

    # Mock the capability check and parameters
    with patch.object(ProviderCapabilities, "supports", return_value=True):
        with patch.object(
            ProviderCapabilities,
            "get_capability_params",
            return_value={
                "param": "format_schema",
                "schema_method": "model_json_schema",
            },
        ):
            result = structured_output_transformer(request, context)
            assert result != request
            assert "format_schema" in result
            assert result["format_schema"] == MockModel.model_json_schema()
