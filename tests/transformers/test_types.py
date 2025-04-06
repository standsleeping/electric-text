from typing import Dict, Any

from electric_text.transformers.types import TransformerFn


def test_transformer_fn_type():
    """Test the TransformerFn type annotation."""

    # Create a function that should match the TransformerFn type
    def test_transformer(
        request: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return request.copy()

    # We can't directly test type annotations at runtime, but we can verify
    # that we can use the function in a context that expects TransformerFn
    transformer: TransformerFn = test_transformer

    # Call the function to verify it works as expected
    request = {"key": "value"}
    context = {"context_key": "context_value"}
    result = transformer(request, context)

    # Verify the function worked correctly
    assert result == request
    assert result is not request  # Should be a copy
