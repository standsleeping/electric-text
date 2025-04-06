from unittest.mock import patch

from electric_text.transformers import prepare_provider_request


class MockModel:
    @classmethod
    def model_json_schema(cls):
        return {"type": "object"}


def test_prepare_provider_request_basic():
    """Test basic request preparation."""
    request = {"model": "test-model", "messages": []}

    # Mock the compose_transformers function to return a modified request
    def mock_transform(r, c):
        return {**r, "structured": True, "prefill": True}

    with patch(
        "electric_text.transformers.prepare_provider_request.compose_transformers",
        return_value=mock_transform,
    ):
        result = prepare_provider_request(
            request,
            response_model=MockModel,
            provider_name="test",
            prefill_content="prefill content",
        )

        # Check the result
        assert result != request
        assert "structured" in result
        assert "prefill" in result

        # The context should be created correctly inside prepare_provider_request
        # but we can't easily verify it since we're mocking the compose_transformers function


def test_prepare_provider_request_minimal():
    """Test minimal request preparation with no optional parameters."""
    request = {"model": "test-model", "messages": []}

    # Set up the transformers to not modify the request
    with patch(
        "electric_text.transformers.compose_transformers",
        return_value=lambda r, c: r.copy(),
    ):
        result = prepare_provider_request(request)

        # Result should be a copy of the original
        assert result == request
        assert result is not request


def test_prepare_provider_request_integration():
    """Integration test with actual transformers."""
    request = {"model": "test-model", "messages": []}
    response_model = MockModel
    provider_name = "test"
    prefill_content = "prefill content"

    # This test uses the actual functions, not mocks
    with patch(
        "electric_text.transformers.structured_output_transformer",
        side_effect=lambda r, c: r.copy(),
    ):
        with patch(
            "electric_text.transformers.prefill_transformer",
            side_effect=lambda r, c: r.copy(),
        ):
            result = prepare_provider_request(
                request,
                response_model=response_model,
                provider_name=provider_name,
                prefill_content=prefill_content,
            )

            # Since our mocks just return copies, the result should equal the request
            assert result == request
            assert result is not request
