import pytest
from pathlib import Path
from electric_text.prompting.data.prompt_config import PromptConfig


def test_prompt_config_model():
    """Test the PromptConfig model directly."""
    # Create a PromptConfig
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
        schema_path="/path/to/schema.json",
    )

    # Check the properties
    assert config.name == "test"
    assert config.description == "Test description"
    assert config.system_message_path == "/path/to/system_message.txt"
    assert config.schema_path == "/path/to/schema.json"

    # Test with optional field omitted
    config_no_schema = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
    )

    assert config_no_schema.schema_path is None


def test_get_system_message(temp_prompt_dir, monkeypatch):
    """Test that get_system_message correctly loads the system message."""
    # Create a config with a path to an actual file
    system_message_path = Path(temp_prompt_dir) / "test_system_message.txt"
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path=str(system_message_path),
    )

    # Get the system message
    system_message = config.get_system_message()

    # Check that it matches what we wrote
    assert system_message == "This is a test system message."


def test_get_schema(temp_prompt_dir, monkeypatch):
    """Test that get_schema correctly loads the JSON schema."""
    # Create a config with a path to an actual schema file
    schema_path = Path(temp_prompt_dir) / "schemas" / "test_schema.json"
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path=str(Path(temp_prompt_dir) / "test_system_message.txt"),
        schema_path=str(schema_path),
    )

    # Get the schema
    schema = config.get_schema()

    # Check that it matches what we wrote
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "response" in schema["properties"]
    assert schema["properties"]["response"]["type"] == "string"
    assert schema["required"] == ["response"]


def test_get_schema_none():
    """Test that get_schema returns None when no schema is specified."""
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
    """Test error handling when the system message file doesn't exist."""
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/nonexistent/file.txt",
    )

    # This should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        config.get_system_message()


def test_nonexistent_schema_file():
    """Test error handling when the schema file doesn't exist."""
    config = PromptConfig(
        name="test",
        description="Test description",
        system_message_path="/path/to/system_message.txt",
        schema_path="/path/to/nonexistent/schema.json",
    )

    # This should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        config.get_schema()
