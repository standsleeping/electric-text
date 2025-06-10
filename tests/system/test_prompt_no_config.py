"""
Configuration Source: Config file
Prompt Config: No
Streaming: No
Tool Usage: None
Output Structure: Plain text
"""

import pytest
from textwrap import dedent

from electric_text.prompting.functions.generate import generate
from electric_text.prompting.data.system_output_type import SystemOutputType
from tests.boundaries import (
    mock_boundaries,
    ollama_api_response,
)


@pytest.mark.asyncio
async def test_prompt_no_config():
    """System test: prompt config is not specified"""

    expected_haiku = dedent(
        """
        Line one
        Line two
        Line three
        """
    ).strip()

    mocks = {
        "http://localhost:11434/api/chat": ollama_api_response(expected_haiku),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={"ELECTRIC_TEXT_CONFIG": "examples/config.yaml"},
    ):
        result = await generate(
            text_input="Write a haiku.",
            provider_name="ollama",
            model_name="llama3.1:8b",
            log_level="ERROR",
        )

        assert result.response_type == SystemOutputType.TEXT
        assert result.text is not None
        assert result.text.content == expected_haiku
