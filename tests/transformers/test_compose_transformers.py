from typing import Dict, Any

from electric_text.transformers import compose_transformers


def test_compose_transformers_empty():
    """Test composing with no transformers."""
    transform = compose_transformers()
    request = {"key": "value"}
    context = {}

    result = transform(request, context)
    assert result == request
    assert result is not request  # Should be a copy


def test_compose_transformers_single():
    """Test composing with a single transformer."""

    def transformer1(req: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = req.copy()
        result["transformed1"] = True
        return result

    transform = compose_transformers(transformer1)
    request = {"key": "value"}
    context = {}

    result = transform(request, context)
    assert result != request
    assert result["key"] == "value"
    assert result["transformed1"] is True


def test_compose_transformers_multiple():
    """Test composing multiple transformers."""

    def transformer1(req: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = req.copy()
        result["transformed1"] = True
        return result

    def transformer2(req: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = req.copy()
        result["transformed2"] = True
        return result

    transform = compose_transformers(transformer1, transformer2)
    request = {"key": "value"}
    context = {}

    result = transform(request, context)
    assert result != request
    assert result["key"] == "value"
    assert result["transformed1"] is True
    assert result["transformed2"] is True


def test_compose_transformers_order():
    """Test that transformers are applied in the correct order."""

    def transformer1(req: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = req.copy()
        result["order"] = "first"
        return result

    def transformer2(req: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        result = req.copy()
        if "order" in result:
            result["order"] = "second"
        return result

    transform = compose_transformers(transformer1, transformer2)
    request = {}
    context = {}

    result = transform(request, context)
    assert result["order"] == "second"

    # Try reverse order
    transform_reverse = compose_transformers(transformer2, transformer1)
    result_reverse = transform_reverse(request, context)
    assert result_reverse["order"] == "first"
