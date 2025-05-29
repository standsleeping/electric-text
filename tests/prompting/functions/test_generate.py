import pytest


from electric_text.prompting.functions.generate import generate
from electric_text.prompting.data.system_output_type import SystemOutputType


@pytest.mark.asyncio
async def test_generate_basic(mock_basic_response):
    """Generate text with basic parameters."""
    mock_basic_response()

    # Call the function with real integration
    result = await generate(
        text_input="Hello, test!", provider_name="ollama", model_name="llama3.1:8b"
    )

    # Verify the result
    assert result.response_type == SystemOutputType.TEXT
    assert result.text is not None
    assert result.text.content == "Hello, world!"


@pytest.mark.asyncio
async def test_generate_with_streaming(mock_streaming_response):
    """Generate text with streaming enabled."""
    mock_streaming_response()

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
async def test_generate_with_tool_boxes(mock_basic_response):
    """Generate text with tool boxes parameter."""
    mock_basic_response("Tool-enabled response")

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
async def test_generate_with_prompt_name(
    mock_basic_response, temp_prompt_dir, monkeypatch
):
    """Generate text with a custom prompt name."""
    # Set the prompt directory environment variable
    monkeypatch.setenv("ELECTRIC_TEXT_PROMPT_DIRECTORY", temp_prompt_dir)

    mock_basic_response("Custom prompt response")

    result = await generate(
        text_input="Test input",
        provider_name="ollama",
        model_name="llama3.1:8b",
        prompt_name="test_prompt",
    )

    assert result.response_type == SystemOutputType.TEXT
    assert result.text is not None
    assert result.text.content == "Custom prompt response"
