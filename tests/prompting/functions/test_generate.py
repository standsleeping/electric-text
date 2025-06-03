import pytest
from pathlib import Path

from electric_text.prompting.functions.generate import generate
from electric_text.prompting.data.system_output_type import SystemOutputType
from tests.boundaries import (
    mock_http,
    mock_boundaries,
    ollama_api_response,
    ollama_streaming_response,
    MockFileSystem,
    MockFile,
)


@pytest.mark.asyncio
async def test_generate_basic():
    """Generate text with basic parameters."""
    with mock_http() as http:
        http.mock_post("http://localhost:11434/api/chat", ollama_api_response())

        # Call the function with real integration
        result = await generate(
            text_input="Hello, test!", provider_name="ollama", model_name="llama3.1:8b"
        )

        # Verify the result
        assert result.response_type == SystemOutputType.TEXT
        assert result.text is not None
        assert result.text.content == "Hello, world!"


@pytest.mark.asyncio
async def test_generate_with_streaming():
    """Generate text with streaming enabled."""
    with mock_http() as http:
        http.mock_post("http://localhost:11434/api/chat", ollama_streaming_response())

        # Call the function with streaming enabled
        result_generator = await generate(
            text_input="Hello, streaming test!",
            provider_name="ollama",
            model_name="llama3.1:8b",
            stream=True,
        )

        # Collect all streaming results
        chunks = []
        async for chunk in result_generator:
            chunks.append(chunk)

        # Verify we got multiple chunks
        assert len(chunks) >= 1

        # Verify each chunk is a SystemOutput
        for chunk in chunks:
            assert chunk.response_type == SystemOutputType.TEXT
            assert chunk.text is not None


@pytest.mark.asyncio
async def test_generate_with_tool_boxes():
    """Generate text with tool boxes parameter."""
    with mock_http() as http:
        http.mock_post(
            "http://localhost:11434/api/chat",
            ollama_api_response("Tool-enabled response"),
        )

        result = await generate(
            text_input="What's the weather?",
            provider_name="ollama",
            model_name="llama3.1:8b",
            tool_boxes="test_box",
        )

        assert result.response_type == SystemOutputType.TEXT
        assert result.text is not None
        assert result.text.content == "Tool-enabled response"


@pytest.mark.asyncio
async def test_generate_with_prompt_name():
    """Generate text with a custom prompt name."""
    # Create test file structure for prompt configs
    file_structure = MockFileSystem(
        [
            MockFile(Path("test_system_message.txt"), "This is a test system message."),
            MockFile(
                Path("schemas/test_schema.json"),
                {
                    "type": "object",
                    "properties": {"response": {"type": "string"}},
                    "required": ["response"],
                },
                is_json=True,
            ),
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
        ]
    )

    with mock_boundaries(
        http_mocks={
            "http://localhost:11434/api/chat": ollama_api_response(
                "Custom prompt response"
            )
        },
        filesystem=file_structure,
        env_vars={},
    ) as (_, temp_dir):
        # Set the prompt directory environment variable to our temp directory
        from tests.boundaries import mock_env

        with mock_env({"ELECTRIC_TEXT_PROMPT_DIRECTORY": str(temp_dir)}):
            result = await generate(
                text_input="Test input",
                provider_name="ollama",
                model_name="llama3.1:8b",
                prompt_name="test_prompt",
            )

            assert result.response_type == SystemOutputType.TEXT
            assert result.text is not None
            assert result.text.content == "Custom prompt response"
