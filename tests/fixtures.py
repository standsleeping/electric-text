import os
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory


@pytest.fixture
def clean_env():
    """Fixture to save and restore environment variables."""
    # Save current environment
    env_backup = os.environ.copy()

    # Clear relevant environment variables
    for key in list(os.environ.keys()):
        if "_PROVIDER_NAME_SHORTHAND" in key or "_MODEL_SHORTHAND_" in key:
            del os.environ[key]

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)


@pytest.fixture
def temp_prompt_dir():
    """Fixture that creates a temporary directory with sample prompt configs."""
    with TemporaryDirectory() as temp_dir:
        # Create the directory structure
        temp_dir_path = Path(temp_dir)
        schema_dir = temp_dir_path / "schemas"
        schema_dir.mkdir()

        # Create a test schema file
        test_schema = {
            "type": "object",
            "properties": {"response": {"type": "string"}},
            "required": ["response"],
        }
        schema_path = schema_dir / "test_schema.json"
        with open(schema_path, "w") as f:
            json.dump(test_schema, f)

        # Create a test system message file
        system_message = "This is a test system message."
        system_message_path = temp_dir_path / "test_system_message.txt"
        with open(system_message_path, "w") as f:
            f.write(system_message)

        # Create a test prompt config
        test_config = {
            "name": "test_prompt",
            "description": "Test prompt description",
            "system_message_path": str(system_message_path),
            "schema_path": str(schema_path),
        }
        config_path = temp_dir_path / "test_prompt.json"
        with open(config_path, "w") as f:
            json.dump(test_config, f)

        # Create a prompt config without schema
        test_config_no_schema = {
            "name": "test_prompt_no_schema",
            "description": "Test prompt without schema",
            "system_message_path": str(system_message_path),
        }
        config_path_no_schema = temp_dir_path / "test_prompt_no_schema.json"
        with open(config_path_no_schema, "w") as f:
            json.dump(test_config_no_schema, f)

        yield temp_dir


@pytest.fixture
def invalid_prompt_dir():
    """Fixture that creates a temporary directory with invalid prompt configs."""
    with TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Create an invalid JSON file (syntax error)
        invalid_json_path = temp_dir_path / "invalid_json.json"
        with open(invalid_json_path, "w") as f:
            f.write("{invalid json}")

        # Create a prompt config with missing required field
        missing_field_config = {
            "name": "missing_field",
            # Missing description
            "system_message_path": "/path/to/nonexistent/file.txt",
        }

        missing_field_path = temp_dir_path / "missing_field.json"

        with open(missing_field_path, "w") as f:
            json.dump(missing_field_config, f)

        # Create a valid config for comparison
        valid_config = {
            "name": "valid_config",
            "description": "Valid config description",
            "system_message_path": str(temp_dir_path / "dummy.txt"),
        }

        valid_config_path = temp_dir_path / "valid_config.json"

        with open(valid_config_path, "w") as f:
            json.dump(valid_config, f)

        # Create the dummy system message file
        dummy_system_message_path = temp_dir_path / "dummy.txt"

        with open(dummy_system_message_path, "w") as f:
            f.write("Dummy system message")

        yield temp_dir
