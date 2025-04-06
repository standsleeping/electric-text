from unittest.mock import patch

from electric_text.transformers import prefill_transformer
from electric_text.capabilities import ProviderCapabilities


class MockModel:
    @classmethod
    def model_json_schema(cls):
        return {"type": "object"}


def test_prefill_transformer_no_prefill_needed():
    """Test when no prefill is needed (no model or content)."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test"}

    result = prefill_transformer(request, context)
    assert result == request
    assert result is not request  # Should be a copy


def test_prefill_transformer_unsupported():
    """Test with a provider that doesn't support prefill."""
    request = {"model": "test-model", "messages": []}
    context = {
        "provider_name": "unsupported",
        "response_model": MockModel,
        "prefill_content": "test content",
    }

    with patch.object(ProviderCapabilities, "supports", return_value=False):
        result = prefill_transformer(request, context)
        assert result == request
        assert result is not request  # Should be a copy


def test_prefill_transformer_structured_param():
    """Test with a provider that supports structured prefill flag."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test", "response_model": MockModel}

    with patch.object(ProviderCapabilities, "supports", return_value=True):
        with patch.object(
            ProviderCapabilities,
            "get_capability_params",
            return_value={
                "structured_param": "structured_prefill",
                "structured_value": True,
            },
        ):
            result = prefill_transformer(request, context)
            assert result != request
            assert "structured_prefill" in result
            assert result["structured_prefill"] is True


def test_prefill_transformer_content_param():
    """Test with a provider that supports content prefill."""
    request = {"model": "test-model", "messages": []}
    context = {"provider_name": "test", "prefill_content": "prefill content here"}

    with patch.object(ProviderCapabilities, "supports", return_value=True):
        with patch.object(
            ProviderCapabilities,
            "get_capability_params",
            return_value={"param": "prefill_content"},
        ):
            result = prefill_transformer(request, context)
            assert result != request
            assert "prefill_content" in result
            assert result["prefill_content"] == "prefill content here"
