import pytest
from textwrap import dedent
from electric_text.prompting.data.prompt_config import PromptConfig
from electric_text.clients.data.model_load_error import ModelLoadError
from tests.boundaries import mock_filesystem, full_prompt_config


def test_prompt_config_model():
    """Test the PromptConfig model directly."""
    # Create a PromptConfig
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
        model_path="/path/to/model.py",
    )

    # Check the properties
    assert config.name == "test"
    assert config.description == "Test description"
    assert config.system_message_path == "/path/to/system_message.txt"
    assert config.model_path == "/path/to/model.py"

    # Test with optional field omitted
    config_no_model = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
    )

    assert config_no_model.model_path is None


def test_get_system_message():
    """Loads system message from file."""
    with mock_filesystem(full_prompt_config()) as temp_dir:
        # Create a config with a path to an actual file
        system_message_path = temp_dir / "test_system_message.txt"
        config = PromptConfig(
            name="test",
            description="Test description",
            system_message_path=str(system_message_path),
        )

        # Get the system message
        system_message = config.get_system_message()

        # Check that it matches what we wrote
        assert system_message == "This is a test system message."


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


def test_get_model_class():
    """Loads Pydantic model class from file."""
    with mock_filesystem(full_prompt_config()) as temp_dir:
        # Create a model file
        model_dir = temp_dir / "models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "test_model.py"
        write_test_model_file(model_path)

        # Create a config with a path to the model file
        config = PromptConfig(
            name="test",
            description="Test description",
            system_message_path=str(temp_dir / "test_system_message.txt"),
            model_path=str(model_path),
        )

        # Get the model class
        result = config.get_model_class()

        # Check that it's valid
        assert result.is_valid
        assert result.model_class is not None
        assert result.error is None
        assert hasattr(result.model_class, "model_json_schema")

        # Check the model has the expected fields
        model_fields = result.model_class.model_fields
        assert "response" in model_fields
        assert "details" in model_fields


def test_get_schema_from_model():
    """Returns schema from Pydantic model."""
    with mock_filesystem(full_prompt_config()) as temp_dir:
        # Create a model file
        model_dir = temp_dir / "models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "test_model.py"
        write_test_model_file(model_path)

        # Create a config with a path to the model file
        config = PromptConfig(
            name="test",
            description="Test description",
            system_message_path=str(temp_dir / "test_system_message.txt"),
            model_path=str(model_path),
        )

        # Get the schema
        schema = config.get_schema()

        # Check the schema
        assert schema is not None
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "response" in schema["properties"]
        assert schema["properties"]["response"]["type"] == "string"
        assert "details" in schema["properties"]
        assert "required" in schema
        assert "response" in schema["required"]


def test_get_schema_none():
    """Returns None when no model is specified."""
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
    )

    # Get the schema
    schema = config.get_schema()

    # Check that it's None
    assert schema is None


def test_nonexistent_system_message_file():
    """Raises FileNotFoundError when system message file doesn't exist."""
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/nonexistent/file.txt",
    )

    # This should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        config.get_system_message()


def test_nonexistent_model_file():
    """Returns error when model file doesn't exist."""
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
        model_path="/path/to/nonexistent/model.py",
    )

    # This should return a ModelResult with an error
    result = config.get_model_class()
    assert not result.is_valid
    assert result.error == ModelLoadError.OTHER
    assert "Error loading validation model" in result.error_message

    # get_schema should return None
    schema = config.get_schema()
    assert schema is None


def test_invalid_model_file():
    """Returns error with invalid model file containing no Pydantic model."""
    with mock_filesystem(full_prompt_config()) as temp_dir:
        # Create an invalid model file (no Pydantic model)
        model_dir = temp_dir / "models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "invalid_model.py"

        with open(model_path, "w") as f:
            f.write("# This file contains no Pydantic model\n")

        # Create a config with a path to the invalid model file
        config = PromptConfig(
            name="test",
            description="Test description",
            system_message_path=str(temp_dir / "test_system_message.txt"),
            model_path=str(model_path),
        )

        # Get the model class
        result = config.get_model_class()

        # Check that it's invalid with the expected error
        assert not result.is_valid
        assert result.error == ModelLoadError.NO_MODEL
        assert "No validation model found" in result.error_message
