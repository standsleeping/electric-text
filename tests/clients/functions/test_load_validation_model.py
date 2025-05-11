import tempfile
from pathlib import Path
from textwrap import dedent
from electric_text.clients.functions.load_validation_model import load_validation_model


def write_test_model_file(path):
    """Write a test validation model file for testing."""
    model_code = dedent("""
    from pydantic import BaseModel
    from typing import Optional, List

    class TestResponse(BaseModel):
        response: str
        details: Optional[List[str]] = None
        
        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "response": "This is a test response",
                        "details": ["detail1", "detail2"]
                    }
                ]
            }
        }
    """)
    with open(path, "w") as f:
        f.write(model_code)


def write_invalid_model_file(path):
    """Write a file without a validation model for testing."""
    with open(path, "w") as f:
        f.write("# This file contains no validation model\n")


def test_load_validation_model():
    """Load a validation model from a file successfully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "test_model.py"
        write_test_model_file(model_path)

        # Load the model
        result = load_validation_model(str(model_path))

        # Check that it loaded successfully
        assert result.is_valid
        assert result.model_class is not None
        assert result.error is None

        # Check the model has the expected attributes and methods
        assert hasattr(result.model_class, "model_json_schema")
        assert hasattr(result.model_class, "model_fields")

        # Check we can instantiate the model
        model_instance = result.model_class(response="Test")
        assert model_instance.response == "Test"


def test_load_nonexistent_model_file():
    """Test error handling when the model file doesn't exist."""
    result = load_validation_model("/path/to/nonexistent/model.py")

    # Check that it failed with the expected error
    assert not result.is_valid
    assert result.error == "OTHER"
    assert "Error loading validation model" in result.error_message


def test_load_invalid_model_file():
    """Test error handling with an invalid model file (no validation model)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "invalid_model.py"
        write_invalid_model_file(model_path)

        # Load the model
        result = load_validation_model(str(model_path))

        # Check that it failed with the expected error
        assert not result.is_valid
        assert result.error == "NO_MODEL"
        assert "No validation model found" in result.error_message
