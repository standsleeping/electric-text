"""
Configuration Source: Config file
Prompt Config: Yes (poetry)
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
async def test_poetry_with_prompt_config():
    """System test: poetry prompt config is specified"""

    expected_poem = dedent(
        """
        Line one
        Line two
        Line three
        """
    ).strip()

    mocks = {
        "http://localhost:11434/api/chat": ollama_api_response(expected_poem),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={
            "ELECTRIC_TEXT_CONFIG": "examples/config.yaml",
        },
    ):
        result = await generate(
            text_input="Some text",
            provider_name="ollama",
            model_name="llama3.1:8b",
            prompt_name="poetry",
            log_level="ERROR",
        )

        assert result.response_type == SystemOutputType.TEXT
        assert result.text is not None
        assert result.text.content == expected_poem
