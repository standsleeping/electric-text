import json
import pytest
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch
from electric_text.prompting.functions.get_prompt_list import get_prompt_list
from electric_text.prompting.data.prompt_config import PromptConfig
from tests.boundaries import mock_filesystem, mock_env, MockFileSystem, MockFile
from electric_text.prompting.functions.get_prompt_directory import (
    PROMPT_DIR_NOT_CONFIGURED_MSG,
)


def create_prompt_test_structure():
    """Create a test file structure for prompt configs."""
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
        """).strip()

    system_message = "This is a test system message."

    test_schema = {
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    }

    return MockFileSystem(
        [
            # System message file
            MockFile(Path("test_system_message.txt"), system_message),
            # Model file
            MockFile(Path("models/test_model.py"), model_code),
            # Schema file
            MockFile(Path("schemas/test_schema.json"), test_schema, is_json=True),
            # Config with model_path
            MockFile(
                Path("test_prompt_model.json"),
                {
                    "name": "test_prompt_model",
                    "description": "Test prompt with Pydantic model",
                    "system_message_path": "test_system_message.txt",
                    "model_path": "models/test_model.py",
                },
                is_json=True,
            ),
            # Config with legacy schema_path
            MockFile(
                Path("test_prompt_schema.json"),
                {
                    "name": "test_prompt_schema",
                    "description": "Test prompt with legacy schema",
                    "system_message_path": "test_system_message.txt",
                    "schema_path": "schemas/test_schema.json",
                },
                is_json=True,
            ),
            # Config without model/schema
            MockFile(
                Path("test_prompt_no_model.json"),
                {
                    "name": "test_prompt_no_model",
                    "description": "Test prompt without model",
                    "system_message_path": "test_system_message.txt",
                },
                is_json=True,
            ),
        ]
    )


def create_legacy_prompt_structure():
    """Create legacy test structure matching temp_prompt_dir fixture."""
    test_schema = {
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    }

    system_message = "This is a test system message."

    return MockFileSystem(
        [
            # System message file
            MockFile(Path("test_system_message.txt"), system_message),
            # Schema file
            MockFile(Path("schemas/test_schema.json"), test_schema, is_json=True),
            # Config with schema_path (legacy)
            MockFile(
                Path("test_prompt.json"),
                {
                    "name": "test_prompt",
                    "description": "Test prompt description",
                    "system_message_path": "test_system_message.txt",
                    "schema_path": "schemas/test_schema.json",
                },
                is_json=True,
            ),
            # Config without schema
            MockFile(
                Path("test_prompt_no_schema.json"),
                {
                    "name": "test_prompt_no_schema",
                    "description": "Test prompt without schema",
                    "system_message_path": "test_system_message.txt",
                },
                is_json=True,
            ),
        ]
    )


def create_invalid_prompt_structure():
    """Create test structure with invalid prompt configs."""
    return MockFileSystem(
        [
            # Invalid JSON file
            MockFile(Path("invalid_json.json"), "{invalid json}"),
            # Config with missing field
            MockFile(
                Path("missing_field.json"),
                {
                    "name": "missing_field",
                    "system_message_path": "/path/to/nonexistent/file.txt",
                },
                is_json=True,
            ),
            # Valid config
            MockFile(
                Path("valid_config.json"),
                {
                    "name": "valid_config",
                    "description": "Valid config description",
                    "system_message_path": "dummy.txt",
                },
                is_json=True,
            ),
            # Dummy system message file
            MockFile(Path("dummy.txt"), "Dummy system message"),
        ]
    )


def test_get_prompt_list_with_models():
    """Test that get_prompt_list correctly loads prompt configs with Pydantic models."""
    file_structure = create_prompt_test_structure()

    with mock_filesystem(file_structure) as temp_dir:
        # Set environment variable to point to temp directory
        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
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
                config
                for config in prompt_configs
                if config.name == "test_prompt_model"
            )

            test_prompt_schema = next(
                config
                for config in prompt_configs
                if config.name == "test_prompt_schema"
            )

            test_prompt_no_model = next(
                config
                for config in prompt_configs
                if config.name == "test_prompt_no_model"
            )

            # Check test_prompt_model properties
            assert test_prompt_model.description == "Test prompt with Pydantic model"
            system_message_name = Path(test_prompt_model.system_message_path).name
            assert system_message_name == "test_system_message.txt"
            assert Path(test_prompt_model.model_path).name == "test_model.py"

            # Check that legacy schema_path was converted to model_path
            assert test_prompt_schema.description == "Test prompt with legacy schema"
            assert Path(test_prompt_schema.model_path).name == "test_schema.json"

            # Check test_prompt_no_model properties
            assert test_prompt_no_model.description == "Test prompt without model"
            assert test_prompt_no_model.model_path is None


def test_get_prompt_list():
    """Test that get_prompt_list correctly loads prompt configs from JSON files (legacy test)."""
    file_structure = create_legacy_prompt_structure()

    with mock_filesystem(file_structure) as temp_dir:
        # Set environment variable to point to temp directory
        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
            # Capture print output to verify warning message about schema_path
            with patch("builtins.print") as mock_print:
                # Call the function
                prompt_configs = get_prompt_list()

                # Check for deprecation warning
                assert any(
                    "'schema_path'" in str(args[0])
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
                config
                for config in prompt_configs
                if config.name == "test_prompt_no_schema"
            )

            # Check test_prompt properties
            assert test_prompt.description == "Test prompt description"
            system_message_name = Path(test_prompt.system_message_path).name
            assert system_message_name == "test_system_message.txt"

            # Check that schema_path was converted to model_path
            assert Path(test_prompt.model_path).name == "test_schema.json"

            # Check test_prompt_no_schema properties
            assert test_prompt_no_schema.description == "Test prompt without schema"

            # Check that the system message filename is correct
            system_message_name = Path(test_prompt_no_schema.system_message_path).name
            assert system_message_name == "test_system_message.txt"

            # Check that the model path is None
            assert test_prompt_no_schema.model_path is None


def test_get_prompt_list_env_not_set(clean_env):
    """Test that get_prompt_list raises an error when no prompt directory is configured."""
    # Create a config file that doesn't have prompts.directory
    file_structure = MockFileSystem(
        [
            MockFile(
                Path("config.yaml"),
                {
                    "logging": {"level": "INFO"}
                    # No prompts.directory section
                },
                is_json=True,
            )
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        config_path = str(temp_dir / "config.yaml")

        # Clear environment and set config path without prompts directory
        with mock_env(
            {"ELECTRIC_TEXT_CONFIG": config_path},
            clear_prefix="ELECTRIC_TEXT_",
        ):
            # Check that the function raises a ValueError
            with pytest.raises(ValueError, match=PROMPT_DIR_NOT_CONFIGURED_MSG):
                get_prompt_list()


def test_handle_invalid_json():
    """Test that get_prompt_list gracefully handles invalid JSON files."""
    file_structure = create_invalid_prompt_structure()

    with mock_filesystem(file_structure) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
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


def test_no_json_files():
    """Test behavior when the directory has no JSON files."""
    file_structure = MockFileSystem(
        [
            # Non-JSON file
            MockFile(Path("not_json.txt"), "Not a JSON file")
        ]
    )

    with mock_filesystem(file_structure) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
            # This should return an empty list
            prompt_configs = get_prompt_list()
            assert len(prompt_configs) == 0
