import os
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any


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


@pytest.fixture
def temp_tool_configs_dir():
    """Create a temporary directory with sample tool config files for testing."""
    with TemporaryDirectory() as temp_dir:
        # Create tool_boxes.json
        tool_boxes_config = [
            {
                "name": "test_box",
                "description": "Test tool box",
                "tools": ["test_tool1", "test_tool2"],
            },
            {"name": "empty_box", "description": "Empty tool box", "tools": []},
        ]

        with open(os.path.join(temp_dir, "tool_boxes.json"), "w") as f:
            json.dump(tool_boxes_config, f)

        # Create test_tool1.json
        test_tool1 = {
            "name": "test_tool1",
            "description": "Test tool 1",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter 1"}
                },
                "required": ["param1"],
            },
        }

        with open(os.path.join(temp_dir, "test_tool1.json"), "w") as f:
            json.dump(test_tool1, f)

        # Create test_tool2.json
        test_tool2 = {
            "name": "test_tool2",
            "description": "Test tool 2",
            "parameters": {
                "type": "object",
                "properties": {
                    "param2": {"type": "number", "description": "Parameter 2"}
                },
                "required": ["param2"],
            },
        }

        with open(os.path.join(temp_dir, "test_tool2.json"), "w") as f:
            json.dump(test_tool2, f)

        # Set environment variable for testing
        original_env = os.environ.get("USER_TOOL_CONFIGS_DIRECTORY")
        os.environ["USER_TOOL_CONFIGS_DIRECTORY"] = temp_dir

        yield temp_dir

        # Restore original environment variable
        if original_env:
            os.environ["USER_TOOL_CONFIGS_DIRECTORY"] = original_env
        else:
            del os.environ["USER_TOOL_CONFIGS_DIRECTORY"]


def base_openai_response() -> Dict[str, Any]:
    """Return base OpenAI response data used by all fixtures."""
    return {
        "id": "resp_123",
        "object": "response",
        "created_at": 1747012692,
        "status": "completed",
        "model": "gpt-4o-2024-08-06",
        "parallel_tool_calls": True,
        "reasoning": {"effort": None, "summary": None},
        "service_tier": "default",
        "store": True,
        "temperature": 1.0,
        "tool_choice": "auto",
        "tools": [],
        "top_p": 1.0,
        "truncation": "disabled",
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
        "metadata": {},
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "max_output_tokens": None,
        "previous_response_id": None,
        "user": None,
    }


@pytest.fixture
def sample_openai_response() -> Dict[str, Any]:
    """Fixture providing a sample OpenAI response with JSON content."""
    data = base_openai_response()
    data.update(
        {
            "output": [
                {
                    "id": "msg_123",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": '{"key": "value"}',
                        }
                    ],
                    "role": "assistant",
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "description": None,
                    "name": "test_schema",
                    "schema": {"type": "object", "properties": {}},
                    "strict": True,
                }
            },
        }
    )
    return data


@pytest.fixture
def sample_openai_response_with_content() -> Dict[str, Any]:
    """Fixture providing a sample OpenAI response with specific content text."""
    data = base_openai_response()
    data.update(
        {
            "output": [
                {
                    "id": "msg_123",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": "test content",
                        }
                    ],
                    "role": "assistant",
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "test",
                    "schema": {"type": "object"},
                    "strict": True,
                }
            },
        }
    )
    return data


@pytest.fixture
def sample_openai_response_with_plain_text() -> Dict[str, Any]:
    """Fixture providing a sample OpenAI response with plain text content."""
    data = base_openai_response()
    data.update(
        {
            "output": [
                {
                    "id": "msg_123",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "annotations": [],
                            "text": "test result",
                        }
                    ],
                    "role": "assistant",
                }
            ],
            "text": {
                "format": {
                    "type": "text",
                    "name": "text",
                    "schema": {"type": "string"},
                    "strict": True,
                }
            },
        }
    )
    return data


@pytest.fixture
def sample_prompt_result():
    """Fixture providing a PromptResult with content blocks."""
    from electric_text.clients.data.prompt_result import PromptResult
    from electric_text.providers.data.content_block import (
        ContentBlock,
        ContentBlockType,
        TextData,
    )

    content_blocks = [
        ContentBlock(
            type=ContentBlockType.TEXT, data=TextData(text="Test response content")
        )
    ]

    return PromptResult(
        content_blocks=content_blocks
    )


@pytest.fixture
def sample_prompt_result_with_tool_call():
    """Fixture providing a PromptResult with text and tool call content blocks."""
    from electric_text.clients.data.prompt_result import PromptResult
    from electric_text.providers.data.content_block import (
        ContentBlock,
        ContentBlockType,
        TextData,
        ToolCallData,
    )

    content_blocks = [
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="I'll check the weather for you."),
        ),
        ContentBlock(
            type=ContentBlockType.TOOL_CALL,
            data=ToolCallData(
                name="get_weather",
                input={"location": "Chicago"},
                input_json_string='{"location": "Chicago"}',
            ),
        ),
    ]

    return PromptResult(
        content_blocks=content_blocks
    )


@pytest.fixture
def sample_client_response_unstructured(sample_prompt_result):
    """Fixture providing a ClientResponse for unstructured data."""
    from electric_text.clients.data.client_response import ClientResponse

    return ClientResponse(prompt_result=sample_prompt_result, parse_result=None)


@pytest.fixture
def sample_client_response_with_tool_call(sample_prompt_result_with_tool_call):
    """Fixture providing a ClientResponse with tool call content blocks."""
    from electric_text.clients.data.client_response import ClientResponse

    return ClientResponse(prompt_result=sample_prompt_result_with_tool_call, parse_result=None)
