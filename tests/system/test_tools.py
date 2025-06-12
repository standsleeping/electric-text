"""
Configuration Source: Config file
Prompt Config: No
Streaming: No
Tool Usage: Yes
Output Structure: Plain text
"""

import pytest

from electric_text.prompting.functions.generate import generate
from electric_text.prompting.data.system_output_type import SystemOutputType
from tests.boundaries import (
    mock_boundaries,
    ollama_tool_call_response,
)


@pytest.mark.asyncio
async def test_tools():
    """System test: tool usage without streaming"""

    mocks = {
        "http://localhost:11434/api/chat": ollama_tool_call_response(
            tool_name="get_weather",
            tool_arguments={"city": "Omaha"},
        ),
    }

    with mock_boundaries(
        http_mocks=mocks,
        env_vars={
            "ELECTRIC_TEXT_CONFIG": "examples/config.yaml",
            "ELECTRIC_TEXT_TOOLS_DIRECTORY": "examples/tool_configs",
        },
    ):
        result = await generate(
            text_input="What is the weather in Omaha?",
            provider_name="ollama",
            model_name="llama3.1:8b",
            tool_boxes="meteorology",
            log_level="ERROR",
        )

        assert result.response_type == SystemOutputType.TOOL_CALL
        assert result.tool_call is not None
        assert result.tool_call.name == "get_weather"
        assert result.tool_call.inputs == {"city": "Omaha"}
        assert result.tool_call.output is None
