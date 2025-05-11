import os
import json
import pytest
import tempfile
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch
from electric_text.prompting.functions.get_prompt_list import get_prompt_list
from electric_text.prompting.data.prompt_config import PromptConfig


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


def setup_prompt_dir_with_model(temp_dir):
    """Set up a test directory with a model file instead of a schema file."""
    temp_dir_path = Path(temp_dir)

    # Create models directory
    models_dir = temp_dir_path / "models"
    models_dir.mkdir(exist_ok=True)

    # Create a test model file
    model_path = models_dir / "test_model.py"
    write_test_model_file(model_path)

    # Create a test system message file
    system_message = "This is a test system message."
    system_message_path = temp_dir_path / "test_system_message.txt"
    with open(system_message_path, "w") as f:
        f.write(system_message)

    # Create a test prompt config with model_path
    test_config = {
        "name": "test_prompt_model",
        "description": "Test prompt with Pydantic model",
        "system_message_path": str(system_message_path),
        "model_path": str(model_path),
    }
    config_path = temp_dir_path / "test_prompt_model.json"
    with open(config_path, "w") as f:
        json.dump(test_config, f)

    # Create a legacy prompt config with schema_path
    schema_dir = temp_dir_path / "schemas"
    schema_dir.mkdir(exist_ok=True)
    test_schema = {
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    }
    schema_path = schema_dir / "test_schema.json"
    with open(schema_path, "w") as f:
        json.dump(test_schema, f)

    legacy_config = {
        "name": "test_prompt_schema",
        "description": "Test prompt with legacy schema",
        "system_message_path": str(system_message_path),
        "schema_path": str(schema_path),
    }
    legacy_config_path = temp_dir_path / "test_prompt_schema.json"
    with open(legacy_config_path, "w") as f:
        json.dump(legacy_config, f)

    # Create a prompt config without model/schema
    test_config_no_model = {
        "name": "test_prompt_no_model",
        "description": "Test prompt without model",
        "system_message_path": str(system_message_path),
    }
    config_path_no_model = temp_dir_path / "test_prompt_no_model.json"
    with open(config_path_no_model, "w") as f:
        json.dump(test_config_no_model, f)

    return temp_dir


def test_get_prompt_list_with_models(monkeypatch):
    """Test that get_prompt_list correctly loads prompt configs with Pydantic models."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up a test directory with model files
        setup_prompt_dir_with_model(temp_dir)

        # Set environment variable to point to temp directory
        monkeypatch.setenv("USER_PROMPT_DIRECTORY", temp_dir)

        # Call the function
        prompt_configs = get_prompt_list()

        # Check that we got three prompt configs
        assert len(prompt_configs) == 3

        # Check that the configs have the expected names
        config_names = {config.name for config in prompt_configs}
        assert "test_prompt_model" in config_names
        assert "test_prompt_schema" in config_names
        assert "test_prompt_no_model" in config_names

        test_prompt_model = next(
            config for config in prompt_configs if config.name == "test_prompt_model"
        )

        test_prompt_schema = next(
            config for config in prompt_configs if config.name == "test_prompt_schema"
        )

        test_prompt_no_model = next(
            config for config in prompt_configs if config.name == "test_prompt_no_model"
        )

        # Check test_prompt_model properties
        assert test_prompt_model.description == "Test prompt with Pydantic model"
        assert (
            Path(test_prompt_model.system_message_path).name
            == "test_system_message.txt"
        )
        assert Path(test_prompt_model.model_path).name == "test_model.py"

        # Check that legacy schema_path was converted to model_path
        assert test_prompt_schema.description == "Test prompt with legacy schema"
        assert Path(test_prompt_schema.model_path).name == "test_schema.json"

        # Check test_prompt_no_model properties
        assert test_prompt_no_model.description == "Test prompt without model"
        assert test_prompt_no_model.model_path is None


def test_get_prompt_list(temp_prompt_dir, monkeypatch):
    """Test that get_prompt_list correctly loads prompt configs from JSON files (legacy test)."""
    # Set environment variable to point to temp directory
    monkeypatch.setenv("USER_PROMPT_DIRECTORY", temp_prompt_dir)

    # Capture print output to verify warning message about schema_path
    with patch("builtins.print") as mock_print:
        # Call the function
        prompt_configs = get_prompt_list()

        # Check for deprecation warning
        assert any(
            "'schema_path'" in str(args[0]) in str(args[0])
            for args in mock_print.call_args_list
        )

    # Check that we got two prompt configs
    assert len(prompt_configs) == 2

    # Check that the configs have the expected names
    config_names = {config.name for config in prompt_configs}
    assert "test_prompt" in config_names
    assert "test_prompt_no_schema" in config_names

    test_prompt = next(
        config for config in prompt_configs if config.name == "test_prompt"
    )

    test_prompt_no_schema = next(
        config for config in prompt_configs if config.name == "test_prompt_no_schema"
    )

    # Check test_prompt properties
    assert test_prompt.description == "Test prompt description"
    assert Path(test_prompt.system_message_path).name == "test_system_message.txt"

    # Check that schema_path was converted to model_path
    assert Path(test_prompt.model_path).name == "test_schema.json"

    # Check test_prompt_no_schema properties
    assert test_prompt_no_schema.description == "Test prompt without schema"

    # Check that the system message filename is correct
    system_message_filename = Path(test_prompt_no_schema.system_message_path).name
    expected_filename = "test_system_message.txt"
    assert system_message_filename == expected_filename

    # Check that the model path is None
    assert test_prompt_no_schema.model_path is None


def test_get_prompt_list_env_not_set():
    """Test that get_prompt_list raises an error when USER_PROMPT_DIRECTORY is not set."""
    # Ensure environment variable is not set
    if "USER_PROMPT_DIRECTORY" in os.environ:
        del os.environ["USER_PROMPT_DIRECTORY"]

    # Check that the function raises a ValueError
    with pytest.raises(
        ValueError, match="USER_PROMPT_DIRECTORY environment variable is not set"
    ):
        get_prompt_list()


def test_handle_invalid_json(invalid_prompt_dir, monkeypatch):
    """Test that get_prompt_list gracefully handles invalid JSON files."""
    monkeypatch.setenv("USER_PROMPT_DIRECTORY", invalid_prompt_dir)

    # Capture print output to verify error message
    with patch("builtins.print") as mock_print:
        prompt_configs = get_prompt_list()

        # Check that the error was logged
        assert any(
            "Error loading prompt config from" in str(args[0])
            for args in mock_print.call_args_list
        )

        # Check that we still got the valid config
        assert len(prompt_configs) == 1
        assert prompt_configs[0].name == "valid_config"


def test_no_json_files(monkeypatch):
    """Test behavior when the directory has no JSON files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setenv("USER_PROMPT_DIRECTORY", temp_dir)

        # Create a file with a different extension
        with open(Path(temp_dir) / "not_json.txt", "w") as f:
            f.write("Not a JSON file")

        # This should return an empty list
        prompt_configs = get_prompt_list()
        assert len(prompt_configs) == 0
