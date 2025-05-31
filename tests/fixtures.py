import os
import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import respx
from httpx import Response
from textwrap import dedent
from electric_text.configuration.functions.get_cached_config import (
    get_cached_config,
)


@pytest.fixture(autouse=True)
def fake_http():
    """Block all HTTP requests during tests unless explicitly mocked."""
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
def clean_env():
    """Fixture to save and restore environment variables."""
    # Save current environment
    env_backup = os.environ.copy()

    # Clear all ELECTRIC_TEXT_ environment variables
    for key in list(os.environ.keys()):
        if key.startswith("ELECTRIC_TEXT_"):
            del os.environ[key]

    # Clear config cache
    get_cached_config.cache_clear()

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)

    # Clear config cache again
    get_cached_config.cache_clear()


@pytest.fixture
def basic_ollama_response():
    """Fixture providing a basic Ollama API response for testing."""

    def _create_response(content: str = "Hello, world!", done: bool = True):
        return Response(
            200,
            json={
                "model": "llama3.1:8b",
                "created_at": "2024-01-01T12:00:00Z",
                "message": {"role": "assistant", "content": content},
                "done": done,
            },
        )

    return _create_response


@pytest.fixture
def streaming_ollama_response():
    """Fixture providing a streaming Ollama API response for testing."""

    def _create_streaming_response(chunks: list[str] | None = None):
        if chunks is None:
            chunks = ["Hello", ", streaming", " world!"]

        lines = []
        for i, chunk in enumerate(chunks):
            is_done = i == len(chunks) - 1
            line = {
                "model": "llama3.1:8b",
                "created_at": f"2024-01-01T12:00:0{i}Z",
                "message": {"role": "assistant", "content": chunk},
                "done": is_done,
            }
            lines.append(json.dumps(line))

        return Response(
            200,
            content=dedent("""
                {}
            """)
            .format("\n".join(lines))
            .strip(),
            headers={"content-type": "application/x-ndjson"},
        )

    return _create_streaming_response


@pytest.fixture
def mock_basic_response(fake_http, basic_ollama_response):
    """Fixture that sets up HTTP mocking for basic Ollama responses."""

    def _mock_response(content: str = "Hello, world!", done: bool = True):
        fake_http.post("http://localhost:11434/api/chat").mock(
            return_value=basic_ollama_response(content, done)
        )

    return _mock_response


@pytest.fixture
def mock_streaming_response(fake_http, streaming_ollama_response):
    """Fixture that sets up HTTP mocking for streaming Ollama responses."""

    def _mock_streaming(chunks: list[str] | None = None):
        fake_http.post("http://localhost:11434/api/chat").mock(
            return_value=streaming_ollama_response(chunks)
        )

    return _mock_streaming


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
        original_env = os.environ.get("ELECTRIC_TEXT_TOOLS_DIRECTORY")
        os.environ["ELECTRIC_TEXT_TOOLS_DIRECTORY"] = temp_dir

        yield temp_dir

        # Restore original environment variable
        if original_env:
            os.environ["ELECTRIC_TEXT_TOOLS_DIRECTORY"] = original_env
        else:
            del os.environ["ELECTRIC_TEXT_TOOLS_DIRECTORY"]


@pytest.fixture
def sample_http_log_entry():
    """Sample HttpLogEntry for testing."""
    from electric_text.providers.logging.data.http_log_entry import HttpLogEntry

    return HttpLogEntry(
        timestamp="2024-01-01T12:00:00Z",
        url="https://api.example.com/chat",
        method="POST",
        request_headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
        },
        request_body={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
        },
        response_status=200,
        response_headers={"Content-Type": "application/json"},
        response_body={"choices": [{"message": {"content": "Hi there!"}}]},
        duration_ms=1222.2,
        provider="openai",
        model="gpt-4",
        error=None,
    )


@pytest.fixture
def minimal_http_log_entry():
    """Minimal HttpLogEntry with None values for testing."""
    from electric_text.providers.logging.data.http_log_entry import HttpLogEntry

    return HttpLogEntry(
        timestamp="2024-01-01T12:00:00Z",
        url="https://api.example.com/chat",
        method="GET",
        request_headers={},
        request_body=None,
        response_status=404,
        response_headers={},
        response_body=None,
        duration_ms=100.0,
        provider=None,
        model=None,
        error="HTTP 404",
    )
