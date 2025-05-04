import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from electric_text.prompting.functions.get_prompt_list import get_prompt_list


def test_get_prompt_list(temp_prompt_dir, monkeypatch):
    """Test that get_prompt_list correctly loads prompt configs from JSON files."""
    # Set environment variable to point to temp directory
    monkeypatch.setenv("USER_PROMPT_DIRECTORY", temp_prompt_dir)

    # Call the function
    prompt_configs = get_prompt_list()

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
    assert Path(test_prompt.schema_path).name == "test_schema.json"

    # Check test_prompt_no_schema properties
    assert test_prompt_no_schema.description == "Test prompt without schema"

    # Check that the system message filename is correct
    system_message_filename = Path(test_prompt_no_schema.system_message_path).name
    expected_filename = "test_system_message.txt"
    assert system_message_filename == expected_filename

    # Check that the schema path is None
    assert test_prompt_no_schema.schema_path is None


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
