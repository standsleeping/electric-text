"""
Configuration Source: Config file
Prompt Config: Yes (poetry)
Streaming: Yes
Tool Usage: None
Output Structure: Plain text
"""

import pytest

from electric_text.prompting.functions.generate import generate
from tests.boundaries import (
    mock_boundaries,
    ollama_streaming_response,
)


@pytest.mark.asyncio
async def test_streaming():
    """System test: streaming"""

    mocks = {
        "http://localhost:11434/api/chat": ollama_streaming_response(),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={"ELECTRIC_TEXT_CONFIG": "examples/config.yaml"},
    ):
        result_generator = await generate(
            text_input="Write a haiku.",
            provider_name="ollama",
            model_name="llama3.1:8b",
            prompt_name="poetry",
            stream=True,
            log_level="ERROR",
        )

        chunks = []
        async for chunk in result_generator:
            chunks.append(chunk)

        first = chunks[0]
        assert first.text.content == "Hello"

        second = chunks[1]
        assert second.text.content == "Hello, streaming"

        third = chunks[2]
        assert third.text.content == "Hello, streaming world!"
