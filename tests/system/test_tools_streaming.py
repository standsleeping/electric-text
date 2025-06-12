"""
Configuration Source: Config file
Prompt Config: No
Streaming: Yes
Tool Usage: Yes
Output Structure: Tool call
"""

import pytest

from electric_text.prompting.functions.generate import generate
from electric_text.prompting.data.system_output_type import SystemOutputType
from tests.boundaries import (
    mock_boundaries,
    ollama_streaming_tool_call_response,
)


@pytest.mark.asyncio
async def test_tools_streaming():
    """System test: tool usage with streaming enabled"""

    mocks = {
        "http://localhost:11434/api/chat": ollama_streaming_tool_call_response(
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
        result_generator = await generate(
            text_input="What is the weather in Omaha?",
            provider_name="ollama",
            model_name="llama3.1:8b",
            tool_boxes="meteorology",
            stream=True,
            log_level="ERROR",
        )

        chunks = []
        async for chunk in result_generator:
            chunks.append(chunk)

        last = chunks[-1]

        assert last.response_type == SystemOutputType.TOOL_CALL
        assert last.tool_call is not None
        assert last.tool_call.name == "get_weather"
        assert last.tool_call.inputs == {"city": "Omaha"}
        assert last.tool_call.output is None
