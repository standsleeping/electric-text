from dataclasses import dataclass
from typing import Dict, Any

from electric_text.transformers import get_schema_function


@dataclass
class MockModel:
    name: str
    value: int

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"},
            },
        }


@dataclass
class ModelWithoutSchema:
    field: str


def test_get_schema_function_with_schema():
    """Test getting schema from a model with schema method."""
    schema_fn = get_schema_function(MockModel)
    assert schema_fn is not None
    schema = schema_fn()
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "value" in schema["properties"]


def test_get_schema_function_without_schema():
    """Test getting schema from a model without schema method."""
    schema_fn = get_schema_function(ModelWithoutSchema)
    assert schema_fn is None


def test_get_schema_function_custom_method_name():
    """Test getting schema with custom method name."""
    schema_fn = get_schema_function(MockModel, schema_method_name="model_json_schema")
    assert schema_fn is not None

    # Test with non-existent method
    schema_fn = get_schema_function(MockModel, schema_method_name="nonexistent_method")
    assert schema_fn is None
